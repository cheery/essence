



expr = LayoutChain({
    Buffer: mk_buffer,
    String: mk_string,
    List: mk_list,
    u"alpha:chain": mk_alpha_chain,
    #and so on..
})

def mk_body(body):
    return Column(expr.many(body), body_style)
body = LayoutChain({List: mk_body})

def mk_program_body(program):
    return body(program[0])

program = LayoutChain({
    u"program:body": mk_program_body,
})
