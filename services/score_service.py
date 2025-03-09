

class ScoreService:

    def get_score(self,  fans_count: int, average_read: float) -> int:
        score = self._get_score(fans_count, average_read)
        return score

    def _get_score(self, fans_count: int, avergae_read: float):
        base_core = 0
        if fans_count < 100:
            base_core = 10
        elif fans_count < 500:
            base_core = 20
        elif fans_count < 1000:
            base_core = 30
        elif fans_count < 3000:
            base_core = 40
        elif fans_count < 5000:
            base_core = 50
        elif fans_count < 10000:
            base_core = 60
        elif fans_count < 30000:
            base_core = 70
        elif fans_count < 50000:
            base_core = 80
        else:
            base_core = 90

        rate = avergae_read / fans_count * 100
        weight_score = 0
        if rate <= 5:
            weight_score = rate*4-20
        elif rate <= 10:
            weight_score = rate-5
        elif rate <= 50:
            weight_score = 5+(rate-10)/40*10
        elif rate <= 100:
            weight_score = 15+(rate-50)/50*5
        elif rate <= 200:
            weight_score = 20+(rate-100)/100*10
        else:
            weight_score - 30 + (rate-200)/50

        return max(0, (int)(base_core+weight_score))
