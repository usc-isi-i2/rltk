import sys, os
sys.path.append(os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),
  "../../../rltk")))
import rltk
tk = rltk.init()

print tk.evaluate_indexer("linkage", 'base.json', 'result.json', 4, 4)