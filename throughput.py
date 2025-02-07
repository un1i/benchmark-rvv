import utils


def write_inst(file, inst, ops, total_vecs, v_sz, num_inst):
    cur_vec = v_sz
    for i in range(num_inst):
        new_ops = []
        for k in range(total_vecs):
            new_ops.append(f'v{cur_vec}')
            cur_vec = cur_vec + v_sz if cur_vec + 2 * v_sz <= 32 else v_sz
        for k in range(total_vecs, len(ops)):
            new_ops.append(ops[k])
        str_ops = ', '.join(new_ops)
        utils.gen_inst(file, inst, str_ops)


def gen_inst(file, inst_list, el_sz, v_sz):
    for inst, ops in inst_list:
        if not utils.is_convenient_utils(file, inst, ops, el_sz, v_sz):
            continue
        is_wide_inst = utils.is_int_wide_inst(inst) or utils.is_float_wide_inst(inst)

        utils.gen_cycle_start(file, 100000)

        var_name = utils.get_var_name(inst)
        total_vecs = utils.cnt_vec_registers(ops)
        cur_v_sz = v_sz
        if is_wide_inst:
            cur_v_sz *= 2

        utils.gen_init_registers(file, v_sz, ops, var_name)
        utils.gen_timer(file, "startMeasure1")
        write_inst(file, inst, ops, total_vecs, cur_v_sz, 40)
        utils.gen_timer(file, "finishMeasure2")

        utils.gen_init_registers(file, v_sz, ops, var_name)
        utils.gen_timer(file, 'startMeasure2')
        write_inst(file, inst, ops, total_vecs, cur_v_sz, 80)
        utils.gen_timer(file, "finishMeasure2")

        utils.gen_cycle_finish(file)
        utils.gen_result(file, inst, ops, 40)


def gen_code():
    el_sz, v_sz, inst_list = utils.get_start_parameters()

    output = open(f"throughput_test_{el_sz}_m{v_sz}.cpp", 'w')
    utils.gen_start(output, el_sz, v_sz, "throughput_test")
    gen_inst(output, inst_list, el_sz, v_sz)
    utils.gen_finish(output)


if __name__ == '__main__':
    gen_code()
