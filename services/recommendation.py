from models.recommendation import RecommendedMovie
from repository.recommendation import RecommendationRepository

COLLABORATIVE_WEIGHT = 0.6
STRUCTURAL_WEIGHT = 0.4

class RecommendationService:
    def __init__(self, repository: RecommendationRepository):
        self.repository = repository

    def recommend(self, user_id: str, limit: int) -> list[RecommendedMovie]:
        if not self.repository.has_watch_history(user_id):
            return self._cold_start(user_id, limit)
        return self._hybrid(user_id, limit)

    def _cold_start(self, user_id: str, limit: int) -> list[RecommendedMovie]:
        candidates = self.repository.get_cold_start_candidates(user_id, limit)
        results = []
        for c in candidates:
            structural = self.repository.get_structural_score(user_id, c["movieId"])
            final = round(c["score"] * COLLABORATIVE_WEIGHT + structural * STRUCTURAL_WEIGHT, 4)
            results.append(RecommendedMovie(
                movieId=c["movieId"],
                title=c["title"],
                vote_average=c.get("vote_average"),
                collaborative_score=round(c["score"], 4),
                structural_score=structural,
                final_score=final,
                reason="cold_start",
            ))
        return sorted(results, key=lambda r: r.final_score, reverse=True)

    def _hybrid(self, user_id: str, limit: int) -> list[RecommendedMovie]:
        candidates = self.repository.get_collaborative_candidates(user_id, limit)
        results = []
        for c in candidates:
            structural = self.repository.get_structural_score(user_id, c["movieId"])
            collab = c["collaborative_score"]
            final = round(collab * COLLABORATIVE_WEIGHT + structural * STRUCTURAL_WEIGHT, 4)
            results.append(RecommendedMovie(
                movieId=c["movieId"],
                title=c["title"],
                vote_average=c.get("vote_average"),
                collaborative_score=round(collab, 4),
                structural_score=structural,
                final_score=final,
                reason="collaborative" if structural == 0.0 else "hybrid",
            ))

        results = sorted(results, key=lambda r: r.final_score, reverse=True)
        return results[:limit]
