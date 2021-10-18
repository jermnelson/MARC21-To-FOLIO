from folioclient import FolioClient
import requests.exceptions

from migration_tools.migration_tasks.migration_task_base import MigrationTaskBase
import argparse


def parse_args(task_classes):
    """Parse CLI Arguments"""
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(help="commands", dest="command")
    for task_class in task_classes:
        sub_parser = subs.add_parser(task_class.__name__)
        try:
            task_class.add_cli_arguments(sub_parser)
        except Exception as ee:
            print(task_class.__name__)
            raise ee
    args = parser.parse_args()
    return args


def main():
    try:
        task_classes = inheritors(MigrationTaskBase)
        args = parse_args(task_classes)
        task_class = next(tc for tc in task_classes if tc.__name__ == args.command)
        if "okapi_credentials_string" in args and args.okapi_credentials_string:
            okapi_credentials = args.okapi_credentials_string.split(" ")
            folio_client = FolioClient(
                okapi_credentials[0],
                okapi_credentials[1],
                okapi_credentials[2],
                okapi_credentials[3],
            )
            task_obj = task_class(folio_client, args)
        else:
            task_obj = task_class(args)
        task_obj.do_work()
    except requests.exceptions.SSLError:
        print("\nSSL error. Are you connected to the Internet and the VPN?")


def inheritors(base_class):
    subclasses = set()
    work = [base_class]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


if __name__ == "__main__":
    main()
