import essence.document

err, document = essence.document.load('document/testa.csf')
if err:
    print err
else:
    essence.document.pretty_print(document)

err, document = essence.document.load('document/module')
if err:
    print err
else:
    essence.document.pretty_print(document)

err, document = essence.document.load('document/test.csf')
if err:
    print err
else:
    essence.document.pretty_print(document)

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
    essence.document.save(document, 'document/test.csf')

#fingers = essence.document.count_all(items)['fingers']
#for i in range(fingers):
#    print essence.document.search_finger(items, i)
