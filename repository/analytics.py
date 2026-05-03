from neo4j import Driver


class AnalyticsRepository:
    def __init__(self, driver: Driver):
        self.driver = driver

    def get_movie_financials(self) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)
                WHERE m.budget > 0 AND m.revenue > 0
                RETURN
                    sum(m.budget) AS total_budget,
                    sum(m.revenue) AS total_revenue,
                    round(((sum(m.revenue) - sum(m.budget)) / toFloat(sum(m.budget))) * 100, 2) AS roi_percentage
                """
            )
            return dict(result.single())

    def get_movie_financials_by_id(self, movie_id: int) -> dict | None:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie {movieId: $movieId})
                WHERE m.budget > 0 AND m.revenue > 0
                RETURN
                    m.movieId AS movieId,
                    m.title AS title,
                    m.budget AS budget,
                    m.revenue AS revenue,
                    round(((m.revenue - m.budget) / toFloat(m.budget)) * 100, 2) AS roi_percentage
                """,
                movieId=movie_id,
            )
            record = result.single()
            return dict(record) if record else None

    def get_movies_by_status(self) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)
                WHERE m.status IS NOT NULL AND m.status <> ''
                RETURN m.status AS status, count(m) AS movie_count
                ORDER BY movie_count DESC
                """
            )
            return [dict(r) for r in result]

    def get_movies_by_genre(self) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
                RETURN g.name AS genre, count(m) AS movie_count
                ORDER BY movie_count DESC
                """
            )
            return [dict(r) for r in result]

    def get_release_date_range(self) -> dict:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)
                WHERE m.release_date IS NOT NULL AND m.release_date <> ''
                RETURN
                    min(m.release_date) AS earliest,
                    max(m.release_date) AS latest
                """
            )
            return dict(result.single())

    def get_user_genres(self) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User)-[:INTERESTED_IN]->(g:Genre)
                WITH u.userId AS userId, u.username AS username, collect(g.name) AS genres
                RETURN userId, username, genres
                ORDER BY username
                """
            )
            return [dict(r) for r in result]

    def get_movies_per_company(self) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)-[:BELONGS_TO]->(c:Company)
                WITH c.name AS company, count(m) AS movie_count
                RETURN company, movie_count
                ORDER BY movie_count DESC
                """
            )
            return [dict(r) for r in result]

    def get_top_movies_by_rating(self) -> list[dict]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (m:Movie)
                WHERE m.vote_count >= 100
                RETURN m.movieId AS movieId, m.title AS title,
                       m.vote_average AS vote_average, m.vote_count AS vote_count
                ORDER BY m.vote_average DESC
                LIMIT 10
                """
            )
            return [dict(r) for r in result]
