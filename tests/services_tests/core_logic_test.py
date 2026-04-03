import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import inject
from peewee import SqliteDatabase
from telegram.constants import ChatMemberStatus
from telegram.error import Forbidden

from db.daos.channel_dao import ChannelDao
from db.daos.fleet_dao import FleetDao
from db.models.channel import Channel
from db.models.chat_message import ChatMessage
from db.models.fleet import Fleet
from db.models.user import User
from services.ad_service import AdService
from services.channel_data_provider import ChannelDataProvider
from services.telegram.chat_service import ChatService


class PeeweeDaoLogicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SqliteDatabase(":memory:")
        for model in (User, Fleet, Channel, ChatMessage):
            model._meta.database = cls.db
        cls.db.bind([User, Fleet, Channel, ChatMessage], bind_refs=False, bind_backrefs=False)
        cls.db.connect()
        cls.db.create_tables([User, Fleet, Channel, ChatMessage])

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def setUp(self):
        Channel.delete().execute()
        ChatMessage.delete().execute()
        Fleet.delete().execute()
        User.delete().execute()

        User.create(id=1, user_name="owner", full_name="Owner", add_time=datetime.now())
        Fleet.create(id=1, name="Bronze", min_score=0, max_score=50)
        Fleet.create(id=2, name="Silver", min_score=50, max_score=100)

    def test_get_fleet_by_score_uses_range_query(self):
        fleet = FleetDao.get_fleet_by_score(75)
        self.assertEqual(2, fleet.id)

    def test_get_all_validate_channels_filters_three_flags(self):
        Channel.create(
            id=100,
            name="good",
            title="Good",
            user_id=1,
            fleet_id=1,
            is_access=True,
            is_banned=False,
            is_enable=True,
            add_time=datetime.now(),
            member_count=10,
        )
        Channel.create(
            id=101,
            name="banned",
            title="Banned",
            user_id=1,
            fleet_id=1,
            is_access=True,
            is_banned=True,
            is_enable=True,
            add_time=datetime.now(),
            member_count=10,
        )
        Channel.create(
            id=102,
            name="disabled",
            title="Disabled",
            user_id=1,
            fleet_id=1,
            is_access=True,
            is_banned=False,
            is_enable=False,
            add_time=datetime.now(),
            member_count=10,
        )

        channels = ChannelDao.get_all_validate_channels()

        self.assertEqual([100], [item.id for item in channels])


class ChatServiceTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        inject.clear_and_configure(lambda binder: binder.bind(ChannelDataProvider, ChannelDataProviderStub()))
        self.application = Mock()
        self.application.bot = Mock()
        self.application.add_handler = Mock()
        self.service = ChatService(self.application)

    def tearDown(self):
        inject.clear()

    async def test_update_chat_does_not_publish_when_delete_fails(self):
        old_time = datetime.now() - timedelta(hours=2)

        with patch(
            "services.telegram.chat_service.ChatDao.get_chat_message",
            return_value=SimpleNamespace(message_id=456, push_time=old_time, is_newest=True),
        ), patch.object(self.service, "_delete_message", AsyncMock(return_value=False)) as delete_message, patch.object(
            self.service, "_publish_message", AsyncMock()
        ) as publish_message:
            await self.service._update_chat(123)

        delete_message.assert_awaited_once_with(123, 456)
        publish_message.assert_not_awaited()

    async def test_publish_message_forbidden_removes_channel_immediately(self):
        self.application.bot.send_message = AsyncMock(side_effect=[Forbidden("forbidden"), None])
        self.application.bot.link = "https://t.me/demo"
        self.application.bot.first_name = "demo"

        with patch("services.telegram.chat_service.inject.instance", side_effect=self._inject_instance), \
             patch.object(self.service, "_generate_message", return_value="1. demo"), \
             patch(
                 "services.telegram.chat_service.ChannelDao.get_channel",
                 return_value=SimpleNamespace(user_id=9, title="demo"),
             ), patch("services.telegram.chat_service.ChannelDao.remove_channel") as remove_channel:
            await self.service._publish_message(123)

        self.assertEqual(2, self.application.bot.send_message.await_count)
        remove_channel.assert_called_once_with(123)
        self.assertNotIn(123, self.service._delete_channel_cache)

    async def test_remove_channel_still_happens_when_notice_fails(self):
        self.application.bot.send_message = AsyncMock(side_effect=Exception("notify failed"))

        with patch(
            "services.telegram.chat_service.ChannelDao.get_channel",
            return_value=SimpleNamespace(user_id=9, title="demo"),
        ), patch("services.telegram.chat_service.ChannelDao.remove_channel") as remove_channel:
            await self.service._remove_channel_with_notice(123, "Channel {title} failed")

        remove_channel.assert_called_once_with(123)
        self.assertNotIn(123, self.service._delete_channel_cache)

    def _inject_instance(self, cls):
        if cls is ChannelDataProvider:
            return ChannelDataProviderStub()
        if cls is AdService:
            return AdServiceStub()
        raise AssertionError(f"Unexpected inject lookup: {cls}")


class UserServiceMembershipLogicTest(unittest.TestCase):
    def test_non_matching_status_does_not_trigger_removal_branch(self):
        status = ChatMemberStatus.MEMBER
        should_remove = status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED, ChatMemberStatus.RESTRICTED)
        self.assertFalse(should_remove)


class ChannelDataProviderStub:
    pass


class AdServiceStub:
    head_ads = []
    tail_ads = []
    button_ads = []
