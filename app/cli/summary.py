import click


@click.group("summary", help="Commands for producing summary statistics on data")
def summary():
    pass


@summary.command("all_analysis")
def all_analysis():
    import app.support.summary as s

    s.all_analysis()
    pass
