import argparse
import os
import shlex
import logging
import traceback

from typed_ast import ast3
from graphviz import Source

from core.parser import ClassParser
from core.basecmd import BaseCmd
from core.loader import Loader
from core.writer import DotWriter
from core.serializer import Serializer
from config.config import Config


class PyUML(BaseCmd):

    def __init__(self):
        BaseCmd.__init__(self)
        self.prompt = "pyuml>>>"
        self.intro = """
//  
//                                  _oo8oo_
//                                 o8888888o
//                                 88" . "88
//                                 (| -_- |)
//                                 0\  =  /0
//                               ___/'==='\___
//                             .' \\|     |// '.
//                            / \\|||  :  |||// \\
//                           / _||||| -:- |||||_ \\
//                          |   | \\\  -  /// |   |
//                          | \_|  ''\---/''  |_/ |
//                          \  .-\__  '-'  __/-.  /
//                        ___'. .'  /--.--\  '. .'___
//                     ."" '<  '.___\_<|>_/___.'  >' "".
//                    | | :  `- \`.:`\ _ /`:.`/ -`  : | |
//                    \  \ `-.   \_ __\ /__ _/   .-` /  /
//                =====`-.____`.___ \_____/ ___.`____.-`=====
//                                  `=---=`
//  
//  
//       ~~~~~~above comments from https://github.com/ottomao/bugfreejs/blob/master/testFile_gbk.js have fun:)
//
//       ~~~~~~~Ara BCDE321 Assessment~~~~~~~~~~~~
//                
        """
        self.logger = self._setup_logger()

    def do_exit(self, args):
        """
        Exit
        """
        return -1

    def do_version(self, args):
        """
        Print version info
        """
        config = Config()
        print("\nAra pyuml v" + config.version)

    def do_config(self, args):
        """
        Print config info
        """
        config = Config()
        print("\nAuthor: " + config.author)
        print("\nVersion: " + config.version)
        print("\nUrl: " + config.url)

    def do_2uml(self, args):
        """
        Generate UML diagram from Python source code
        """
        parser = argparse.ArgumentParser(prog='2uml')
        parser.add_argument('Input', help='input file/folder')
        parser.add_argument('Output', help='output folder')
        try:
            splitargs = parser.parse_args(shlex.split(args))

            input_path = splitargs.Input
            loader = Loader()
            code_string_list = loader.load_from_file_or_directory(input_path)

            for index, code_string in enumerate(code_string_list):
                dot_string = self._parse_to_dot(code_string)
                self._render_with_graphviz(index, dot_string)

        except:
            print('Exception: Check the error log')
            self.logger.exception("2uml")
            pass

    def do_persistent(self, args):
        """
        Generate serialization data from AST obj.
        """
        parser = argparse.ArgumentParser(prog='read')
        parser.add_argument('Input', help='input file')
        parser.add_argument('Output', help='output file')
        try:
            splitargs = parser.parse_args(shlex.split(args))
            serializer = Serializer()
            serializer.serialize(1)

        except:
            print('Exception: Check the error log')
            self.logger.exception("persistent")
            pass

    def do_2uml_from_binary(self, args):
        """
        Deserialize AST data from serialization data
        """
        parser = argparse.ArgumentParser(prog='read')
        parser.add_argument('Input', help='input .ast file')
        parser.add_argument('Output', help='output file')

        try:
            splitargs = parser.parse_args(shlex.split(args))
            serializer = Serializer()
            serializer.deserilize()

        except:
            print('Exception: Check the error log')
            self.logger.exception("2uml_from_binary")
            pass

    def _setup_logger(self):
        logging.basicConfig(filename='./log/error.log', level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')
        return logging.getLogger(__name__)

    def _parse_to_dot(self, code_string):
        """
        todo
        """
        tree = ast3.parse(code_string)
        class_parser = ClassParser()
        class_parser.visit(tree)

        dot_string = DotWriter().write(class_parser.classes_list)
        return dot_string

    def _render_with_graphviz(self, index, dot):
        src = Source(dot)
        src.render(format='png', filename="result/uml{}".format(index))


if __name__ == '__main__':
    console = PyUML()
    console.cmdloop()
