from source.components.base_parser import BaseParser
from typed_ast import ast3
from typed_ast.ast3 import ClassDef, Module, FunctionDef
from source.mvc.models.class_recorder import ClassRecorder
from typing import TypeVar, Generic, List


T = TypeVar('T')


class PythonParser(BaseParser, ast3.NodeVisitor, Generic[T]):
    """
    Parese the source code
    """

    def __init__(self, element_type: T):
        super().__init__()
        self.classes_list: List[element_type] = []

    def parse(self, tree):
        self.visit(tree)
        return self.classes_list

    def visit_Module(self, node):
        """
        >>> parser = ClassParser()
        >>> parser.visit_Module(1)
        Traceback (most recent call last):
        AssertionError
        >>> module = Module()
        >>> module.body = {}
        >>> parser.visit_Module(module)
        """
        assert isinstance(node, Module)
        for n in node.body:
            self.visit(n)

    def visit_ClassDef(self, node):
        """
        >>> parser = ClassParser()
        >>> parser.visit_ClassDef(1)
        Traceback (most recent call last):
        AssertionError
        >>> class_def = ClassDef()
        >>> class_def.name = ''
        >>> class_def.bases = {}
        >>> class_def.body = {}
        >>> parser.visit_ClassDef(class_def)
        """
        assert isinstance(node, ClassDef)

        class_recorder = ClassRecorder(node.name, node.bases)

        for child in node.body:
            if isinstance(child, ast3.FunctionDef):

                # argument type
                arguments_info_list = list()
                for arg in child.args.args:
                    if arg.arg == 'self':
                        continue
                    argument_info = ''
                    argument_info += arg.arg
                    if arg.annotation is not None:
                        argument_info += ': ' + arg.annotation.id
                    elif arg.type_comment is not None:
                        argument_info += ': ' + arg.type_comment
                    arguments_info_list.append(argument_info)

                # return type
                return_info = ''
                if isinstance(child.returns, ast3.Name):
                    return_info = ': ' + child.returns.id
                elif child.type_comment is not None:
                    return_info = ": " + child.type_comment

                if child.name.startswith('__'):
                    class_recorder. \
                        methods.append('-{}({}){}'.
                                       format(child.name,
                                              ', '.join(arguments_info_list),
                                              return_info))
                else:
                    class_recorder.methods.append(
                        '+{}({}){}'.format(child.name,
                                           ', '.join(arguments_info_list),
                                           return_info))
                # constructor
                if child.name == '__init__':
                    for code in child.body:
                        if isinstance(code, ast3.Assign):
                            self._parse_date_member_type_comment(
                                code,
                                class_recorder)
                        elif isinstance(code, ast3.AnnAssign):
                            self._parse_date_member_type_annotations(
                                code,
                                class_recorder)

        assert isinstance(class_recorder, ClassRecorder)
        self.classes_list.append(class_recorder)
        ast3.NodeVisitor.generic_visit(self, node)

    def visit_FunctionDef(self, node):
        assert isinstance(node, FunctionDef)
        self.generic_visit(node)

    def clear(self):
        self.classes_list.clear()

    @staticmethod
    def _parse_date_member_type_comment(code, class_recorder):
        # add type comment
        type_comment = ""
        if code.type_comment is not None:
            type_comment = " : " + code.type_comment

        for target in code.targets:
            if not isinstance(target, ast3.Attribute):
                continue

            prefix = '-' if target.attr.startswith('__') else "+"
            class_recorder.members.append("{}{}{}".format(
                prefix, target.attr, type_comment))

    @staticmethod
    def _parse_date_member_type_annotations(code, class_recorder):
        # add type annotations
        assert isinstance(code, ast3.AnnAssign)
        target = code.target
        if not isinstance(target, ast3.Attribute):
            return

        type_annotations = " : " + code.annotation.id

        prefix = '-' if target.attr.startswith('__') else "+"
        class_recorder.members.append("{}{}{}".format(
            prefix, target.attr, type_annotations))
