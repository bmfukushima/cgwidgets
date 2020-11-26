import sys, inspect
import cgwidgets
from cgwidgets import widgets
# def print_classes():
#     for name, obj in inspect.getmembers(sys.modules[widgets]):
#         print(name, obj)
#         if inspect.isclass(obj):
#             print(obj)
#
# print_classes()

a = inspect.getmembers(cgwidgets)
print(a)
b = inspect.getmembers(widgets)
print(b)
print("1")