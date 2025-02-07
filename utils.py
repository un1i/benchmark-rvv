import sys


def gen_start(file, el_sz, v_sz, output_filename):
    file.write(
"""#include <fstream>
int main() {
""")
    file.write(f'    std::ofstream file("{output_filename}_e{el_sz}_m{v_sz}.csv");\n')
    file.write(
"""
    unsigned long startMeasure1, finishMeasure1, startMeasure2, finishMeasure2;
    unsigned long minMeasure1 = 1000000;
    unsigned long minMeasure2 = 1000000;
    int n = 100;
    size_t vl;
""")
    file.write(
        f"""    int{el_sz}_t* int_a, *mask;
    int_a = new int{el_sz}_t[100];
    mask = new int{el_sz}_t[100];
    """)
    file.write(
        """
    for (int i = 0; i < 100; i++) {
        int_a[i] = 1;
        mask[i] = 0;
    }
        """)
    el_type = 'float' if el_sz == 32 else 'double'
    file.write(
        f"""    {el_type} *float_a;
    float_a = new {el_type}[100];
    """)
    file.write(
        """
    for (int i = 0; i < 100; i++) {
        float_a[i] = 1.0;
    }
    """)
    file.write(f'file << "instruction;e{el_sz}_m{v_sz}" << std::endl;\n'
               f'    asm volatile ("vsetvli %0, %1, e{el_sz}, m{v_sz}" : "=r"(vl) : "r"(n));\n')


def gen_finish(file):
    file.write(
"""   delete[] int_a;
   delete[] mask;
   delete[] float_a;
   return 0;
};
""")


def gen_cycle_start(file, num_iteration):
    file.write('    minMeasure1 = 1000000;\n')
    file.write('    minMeasure2 = 1000000;\n')
    file.write(f'    for (int i = 0; i < {num_iteration}; i++) ' + "{\n")


def gen_timer(file, var_timer_name):
    file.write('        asm volatile ("fence");\n')
    file.write(f'        asm volatile ("rdcycle %0" : "=r"({var_timer_name}));\n')


def gen_init_registers(file, v_sz, ops, var_name):
    for i in range(v_sz, 32, v_sz):
        file.write(f'        asm volatile ("vle.v v{i}, (%0)" : "+r"({var_name}));\n')
    for op in ops:
        if op == 't0':
            file.write(f'        asm volatile ("li {op}, 1");\n')
        elif op == 'ft0':
            file.write(f'        asm volatile ("li t0, 0x3F800000");\n')
            file.write(f'        asm volatile ("fmv.w.x {op}, t0");\n')
        elif op == 'v0.t':
            file.write(f'        asm volatile ("vle.v v0, (%0)" : "+r"(mask));\n')


def gen_cycle_finish(file):
    file.write('        minMeasure1 = std::min(minMeasure1, finishMeasure1 - startMeasure1);\n'
               '        minMeasure2 = std::min(minMeasure2, finishMeasure2 - startMeasure2);\n'
               '   }\n')


def gen_result(file, inst, ops, num_inst):
    file.write(f'   file << "{inst} {",".join(ops)};" << double(minMeasure2 - minMeasure1) / {num_inst} << std::endl;\n')


def gen_inst(file, inst, str_ops):
    file.write(f'        asm volatile ("{inst} {str_ops}");\n')


def divide_inst(file):
    inst = []
    for line in file:
        cur_instr, cur_ops = line.split()
        cur_ops = cur_ops.split(',')
        if len(cur_ops) < 3 or (len(cur_ops) == 4 and cur_ops[-1] != 'v0.t'):
            continue
        skip = False
        for i in range(2):
            if cur_ops[i][0] != 'v':
                skip = True
                break
        if skip:
            continue
        inst.append((cur_instr, tuple(cur_ops)))
    return inst


def cnt_vec_registers(ops):
    total_vecs = 0
    for op in ops:
        if op == 'v0' or op == 'v8' or op == 'v16' or op == 'v24':
            total_vecs += 1
    return total_vecs


def write_skip_inst(file, inst, ops):
    file.write(f'   file << "{inst} {",".join(ops)};" << "-" << std::endl;\n')


def is_mask_inst(ops):
    for op in ops:
        if op == 'v0.t':
            return True
    return False


def is_float_inst(inst):
    if 'vf' in inst or ('vmf' in inst and 'vmfirst' not in inst):
        return True
    return False


def is_execute_float(el_sz):
    return el_sz == 32 or el_sz == 64


def is_float_wide_inst(inst):
    if 'fw' in inst or 'fn' in inst:
        return True
    return False


def is_boundary_vector(el_sz, v_sz):
    if el_sz == 64 or v_sz == 8:
        return True


def is_int_wide_inst(inst):
    if 'vn' in inst or 'vw' in inst:
        return True
    return False


def is_convenient_utils(file, inst, ops, el_sz, v_sz):
    if is_float_inst(inst):
        if not is_execute_float(el_sz):
            write_skip_inst(file, inst, ops)
            return False
        if is_float_wide_inst(inst) and is_boundary_vector(el_sz, v_sz):
            write_skip_inst(file, inst, ops)
            return False
    else:
        if is_int_wide_inst(inst) and is_boundary_vector(el_sz, v_sz):
            write_skip_inst(file, inst, ops)
            return False
    return True


def get_var_name(inst):
    if is_float_inst(inst):
        return 'float_a'
    return 'int_a'


def get_start_parameters():
    el_sz = 32
    v_sz = 1
    if len(sys.argv) == 3:
        el_sz = int(sys.argv[1])
        v_sz = int(sys.argv[2])

    inst_file = open("instructions")
    inst_list = divide_inst(inst_file)
    return el_sz, v_sz, inst_list
