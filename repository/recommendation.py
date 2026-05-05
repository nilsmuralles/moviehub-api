from neo4j import Driver

class RecommendationRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def has_watch_history(self, user_id: str) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})-[:WATCHED|RECOMMENDS]->(m:Movie)
                RETURN count(m) > 0 AS has_history
                """,
                userId=user_id,
            )
            record = result.single()
            return record["has_history"] if record else False

    def get_cold_start_candidates(self, user_id: str, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})-[i:INTERESTED_IN]->(g:Genre)<-[:HAS_GENRE]-(m:Movie)
                WHERE NOT (u)-[:WATCHED]->(m)
                WITH m, sum(i.affinity_score) AS genre_affinity
                RETURN
                    m.movieId AS movieId,
                    m.title AS title,
                    m.vote_average AS vote_average,
                    genre_affinity,
                    (genre_affinity * 0.5 + coalesce(m.vote_average, 0) * 0.05) AS score
                ORDER BY score DESC
                LIMIT $limit
                """,
                userId=user_id,
                limit=limit,
            )
            return [dict(r) for r in result]

    def get_collaborative_candidates(self, user_id: str, limit: int) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId})-[:WATCHED|RECOMMENDS]->(m:Movie)
                WITH u, collect(m.movieId) AS user_movies

                MATCH (neighbor:User)-[:WATCHED|RECOMMENDS]->(m2:Movie)
                WHERE neighbor.userId <> $userId
                  AND m2.movieId IN user_movies
                WITH u, user_movies, neighbor, count(m2) AS shared

                MATCH (neighbor)-[:WATCHED|RECOMMENDS]->(candidate:Movie)
                WHERE NOT candidate.movieId IN user_movies

                WITH candidate, shared, size(user_movies) AS user_total,
                     count(DISTINCT neighbor) AS neighbor_count
                WITH candidate,
                     toFloat(shared) / (user_total + neighbor_count - shared) AS jaccard,
                     neighbor_count
                WITH candidate,
                     avg(jaccard) AS collaborative_score
                RETURN
                    candidate.movieId AS movieId,
                    candidate.title AS title,
                    candidate.vote_average AS vote_average,
                    collaborative_score
                ORDER BY collaborative_score DESC
                LIMIT $limit
                """,
                userId=user_id,
                limit=limit * 3,
            )
            return [dict(r) for r in result]

    def get_structural_score(self, user_id: str, movie_id: int) -> float:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {userId: $userId}), (m:Movie {movieId: $movieId})
                MATCH path = shortestPath(
                    (u)-[:WATCHED|INTERESTED_IN|HAS_GENRE|ACTED_IN|DIRECTED*..6]-(m)
                )
                RETURN length(path) AS path_length
                LIMIT 1
                """,
                userId=user_id,
                movieId=movie_id,
            )
            record = result.single()
            if not record:
                return 0.0
            path_length = record["path_length"]
            return round(1.0 / path_length if path_length > 0 else 0.0, 4)
