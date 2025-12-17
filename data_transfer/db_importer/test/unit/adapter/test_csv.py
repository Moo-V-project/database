from db_importer.adapter.csv import read_all_movie_csvs


def test_read_all_movie_csvs(csv_fixtures_dir):
    genres_df, countries_df, companies_df, people_df, movies_df = (
        read_all_movie_csvs(base_path=csv_fixtures_dir / "valid")
    )
