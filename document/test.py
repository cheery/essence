import essence.document
from essence.document import load, pretty_print, save, retag, wrap, unwrap

err, document = load('document/testa.csf')
if err:
    print err
else:
    pretty_print(document)

err, document = load('document/module')
if err:
    print err
else:
    pretty_print(document)

err, document = load('document/test.csf')
if err:
    print err
else:
    pretty_print(document)

#document = essence.document.new([
#    essence.document.block('add', [
#        essence.document.string('num','1'),
#        essence.document.string('num','2'),
#        essence.document.lshard('mul'),
#        essence.document.rshard('mul'),
#    ]),
#])
if document == None:
    print "I have nothing to save"
else:
    save(document, 'document/test.csf')

retag(document, 3, 4, u'sub')
retag(document, 4, 5, u'sub')
retag(document, 0, 6, u'div')
wrap(document, 3, 5)
#unwrap(document, 3, 5)
#essence.document.retag(document, 1, 2, u'float')
pretty_print(document)
