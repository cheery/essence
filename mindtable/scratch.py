from schema import analyzer
from schema.language import language

ndef = analyzer.normalize(language)

inv = analyzer.partial_inversion(ndef)



for key, argv in ndef.items():
    print key
    if argv:
        print '   ' + '\n   '.join(map(repr, argv))

print 'inversion'
print inv

for name, (nxt, in_list, cost) in analyzer.template_chains(inv, analyzer.String):
    if in_list:
        print "%12r[0] > [%r]" % (name, nxt)
    else:
        print "%12r[0] > %r" % (name, nxt)
