import utils


def write_inst(file, inst, ops, num_inst):
    for i in range(num_inst):
        if i % 2 == 0:
            str_ops = ', '.join(ops)
        else:
            tmp = list(ops)
            tmp[0], tmp[1] = tmp[1], tmp[0]
            str_ops = ', '.join(tmp)
        utils.gen_inst(file, inst, str_ops)


def gen_inst(file, inst_list, el_sz, v_sz):
    for inst, ops in inst_list:
        if not utils.is_convenient_utils(file, inst, ops, el_sz, v_sz):
            continue
        utils.gen_cycle_start(file, 1000000)
        var_name = utils.get_var_name(inst)

        utils.gen_init_registers(file, 8, ops, var_name)
        utils.gen_timer(file, "startMeasure1")
        write_inst(file, inst, ops, 20)
        utils.gen_timer(file, "finishMeasure1")

        utils.gen_init_registers(file, 8, ops, var_name)
        utils.gen_timer(file, "startMeasure2")
        write_inst(file, inst, ops, 30)
        utils.gen_timer(file, "finishMeasure2")

        utils.gen_cycle_finish(file)
        utils.gen_result(file, inst, ops, 10)


def gen_code():
    el_sz, v_sz, inst_list = utils.get_start_parameters()
    output = open(f"latency_test_e{el_sz}_m{v_sz}.cpp", 'w')
    utils.gen_start(output, el_sz, v_sz, "latency_test")
    gen_inst(output, inst_list, el_sz, v_sz)
    utils.gen_finish(output)


if __name__ == '__main__':
    gen_code()
