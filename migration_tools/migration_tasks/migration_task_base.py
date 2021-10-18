import logging
import logging.handlers
import os
import time
from abc import abstractmethod
from argparse import ArgumentParser
from datetime import datetime
from migration_tools.helper import Helper

from folioclient import FolioClient


class MigrationTaskBase:
    def __init__(self, folio_client: FolioClient = None, class_name="", log_path=""):
        self.stats = {}
        self.migration_report = {}
        self.folio_client = folio_client
        self.setup_logging(
            self.__class__.__name__, log_path, time.strftime("%Y%m%d-%H%M%S")
        )

    @staticmethod
    def setup_logging(class_name="", log_file_path: str = None, time_stamp=None):
        if not time_stamp:
            time_stamp = time.strftime("%Y%m%d-%H%M%S")
        logger = logging.getLogger()
        logger.handlers = []
        formatter = logging.Formatter("%(levelname)s\t%(message)s\t%(asctime)s")
        stream_handler = logging.StreamHandler()
        logger.setLevel(logging.INFO)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        print(f"LFP:{log_file_path}")
        if log_file_path:
            log_file = os.path.join(
                log_file_path, f"service_task_log_{class_name}_{time_stamp}.log"
            )
            logging.info(f"Writing log file to {log_file}")
            file_formatter = logging.Formatter(
                "%(levelname)s\t%(message)s\t%(asctime)s"
            )
            file_handler = logging.FileHandler(
                filename=log_file,
            )
            # file_handler.addFilter(LevelFilter(0, 20))
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(logging.INFO)
            logging.getLogger().addHandler(file_handler)
        else:
            logging.info("no path, no logfile")
        logger.info("Logging setup")

        if log_file_path:
            debug_log_file = os.path.join(
                log_file_path, f"service_task_debug_log_{class_name}_{time_stamp}.log"
            )
            logging.info(f"Writing DEBUG log files to {debug_log_file}")
            debug_file_formatter = logging.Formatter(
                "%(levelname)s\t%(message)s\t%(asctime)s"
            )
            debug_file_handler = logging.FileHandler(
                filename=debug_log_file,
            )
            # file_handler.addFilter(LevelFilter(0, 20))
            debug_file_handler.setFormatter(debug_file_formatter)
            debug_file_handler.setLevel(logging.DEBUG)
            logging.getLogger().addHandler(debug_file_handler)
        else:
            logging.info("no path, no logfile")
        logger.info("Logging setup")

    def write_migration_report(self, report_file):
        Helper.write_migration_report(report_file, self.migration_report)

    def add_stats(self, measure_to_add):
        if measure_to_add not in self.stats:
            self.stats[measure_to_add] = 1
        else:
            self.stats[measure_to_add] += 1

    def wrap_up(self):
        self.print_stats()
        self.print_migration_report()

    @staticmethod
    def print_dict_to_md_table(my_dict, h1="", h2=""):
        d_sorted = {k: my_dict[k] for k in sorted(my_dict)}
        for k, v in d_sorted.items():
            logging.info(f"{k} | {v}")

    def print_stats(self):
        self.print_dict_to_md_table(self.stats, "Measure", "  #  ")

    def add_to_migration_report(self, header, message_string):
        if header not in self.migration_report:
            self.migration_report[header] = {}
        if message_string not in self.migration_report[header]:
            self.migration_report[header][message_string] = 1
        else:
            self.migration_report[header][message_string] += 1

    def print_migration_report(self):
        for a in self.migration_report:
            logging.info(f"# {a}")
            b = self.migration_report[a]
            sortedlist = [(k, b[k]) for k in sorted(b, key=as_str)]
            for b in sortedlist:
                logging.info(f"{b[0]}\t{b[1]}")

    @staticmethod
    @abstractmethod
    def add_arguments(sub_parser):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def add_cli_arguments(sub_parser):
        raise NotImplementedError

    @staticmethod
    def add_argument(parser, destination, help, widget, **kwargs):
        parser.add_argument(
            dest=destination,
            help=help,
            widget=widget,
            metavar=kwargs.get("metavar"),
            choices=kwargs.get("choices"),
            gooey_options=kwargs.get("gooey_options"),
            action=kwargs.get("action"),
        )

    @staticmethod
    def add_cli_argument(parser: ArgumentParser, destination, help, **kwargs):
        parser.add_argument(dest=destination, help=help, **kwargs)

    @abstractmethod
    def do_work(self):
        raise NotImplementedError

    @staticmethod
    def add_common_arguments(parser):
        parser.add_argument(
            "okapi_credentials_string",
            help="Space delimited string containing "
            "OKAPI_URL TENANT_ID  USERNAME PASSWORD in that order.",
        )


def as_str(s):
    try:
        return str(s), ""
    except ValueError:
        return "", s


class LevelFilter(logging.Filter):
    def __init__(self, low, high):
        self._low = low
        self._high = high
        logging.Filter.__init__(self)

    def filter(self, record):
        return self._low <= record.levelno <= self._high
