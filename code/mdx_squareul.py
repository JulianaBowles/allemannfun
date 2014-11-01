import markdown
from markdown.treeprocessors import Treeprocessor

class SquareUlTreeprocessor(Treeprocessor):
    def modifyUL(self,element):
        if element.tag == 'ul':
            element.set("class", "square")        
        for e in element:
            self.modifyUL(e)
        return element

    def run(self,root):
        self.modifyUL(root)

        return root


class SquareUlExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        """ Insert IdTreeProcessor in tree processors. It should be before toc. """
        ulext = SquareUlTreeprocessor(md)
        ulext.config = self.config
        md.treeprocessors.add("squareul", ulext, "_begin")


def makeExtension(**kwargs):
    return SquareUlExtension(**kwargs)
