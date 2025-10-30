import json
from pathlib import Path

import djclick as click
from django.conf import settings
from movies.utils import clear_movie_data, load_movies_from_data


@click.command()
@click.option("--file", default="data/movies.json", help="Path to movies JSON file")
@click.option("--clear", is_flag=True, help="Clear existing data before loading")
@click.argument("count", type=int, required=False)
def command(file, clear, count):
    """Load movies data from JSON file into the database."""

    if clear:
        click.secho("Clearing existing movie data...", fg="yellow")
        clear_movie_data()
        click.secho("Existing data cleared.", fg="green")

    file_path = Path(settings.BASE_DIR) / file

    if not file_path.exists():
        click.secho(f"Error: File {file_path} not found", fg="red", err=True)
        return

    click.secho(f"Loading movies from {file_path}...", fg="blue")

    with open(file_path) as f:
        movies_data = json.load(f)

    if count is not None:
        movies_data = movies_data[:count]
        click.secho(f"Loading first {count} movies...", fg="cyan")

    (
        total_created_movies,
        total_created_genres,
        total_created_cast,
    ) = load_movies_from_data(movies_data)

    click.secho("\nLoading complete!", fg="green", bold=True)
    click.secho(f"Created {total_created_movies} movies", fg="green")
    click.secho(f"Created {total_created_genres} genres", fg="green")
    click.secho(f"Created {total_created_cast} cast members", fg="green")
