import djclick as click
import pandas as pd


@click.command()
@click.option(
    "--file",
    default="fixtures/order_details.csv",
    help="Path to order details csv file",
)
@click.option("--rows_per_file", default=100000, help="chunksize/rows_per_file")
def command(file, rows_per_file, output_prefix="output_chunk"):
    df_iterator = pd.read_csv(file, chunksize=rows_per_file)

    for i, chunk in enumerate(df_iterator):
        output_filename = f"{output_prefix}_{i+1}.csv"
        chunk.to_csv(
            output_filename, index=False
        )  # index=False prevents writing DataFrame index
