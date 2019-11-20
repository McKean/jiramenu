#!/usr/bin/python3
from jira import JIRA
from rofi import Rofi
from subprocess import Popen, DEVNULL
from os.path import expanduser
import os
import shutil
import configparser
import click


@click.group()
def cli():
    pass


@click.command(help="Runs dmenujira")
@click.option('--debug/--no-debug', default=False)
def show(debug=False):
    r = Rofi()
    config = configparser.ConfigParser()
    config.read(expanduser('~/.dmenujira'))

    auth_jira = JIRA(config['JIRA']['url'], basic_auth=(config['JIRA']['user'], config['JIRA']['password']))

    project_query = 'project=' + config['JIRA']['project']
    issues = auth_jira.search_issues(project_query)

    rofi_list = []
    for issue in issues:
        rofi_list.append(issue.key + ':' + issue.fields.summary)
    index, key = r.select('What Issue?', rofi_list, rofi_args=['-i'])
    if index < 0:
        exit(1)
    ticket_number = rofi_list[index].split(":")[0]

    uri = auth_jira.issue(ticket_number).permalink()
    Popen(['nohup', config['JIRA']['browser'], uri], stdout=DEVNULL, stderr=DEVNULL)


@cli.command(help="creates sample config file")
@click.option("-d", "--dest",
              required=False,
              type=click.Path(),
              default=expanduser("~/.dmenujira"))
def copy_config(dest):
    if os.path.exists(dest):
        raise click.UsageError("Config already exists in {}".format(dest))
    if not os.path.exists(os.path.dirname(dest)):
        raise click.UsageError("Directory doesn't exist: {}".format(os.path.dirname(dest)))

    click.echo("Creating config in {}".format(dest))
    shutil.copy("./dmenujira.conf", dest)


cli.add_command(show)
cli.add_command(copy_config)

if __name__ == '__main__':
    cli()
