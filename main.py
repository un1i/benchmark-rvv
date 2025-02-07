def main():
    input_file = open("C:\\Users\\olimp.ITMM\\Downloads\\tmp.txt")
    output_file = open("C:\\Users\\olimp.ITMM\\Downloads\\instr", 'w')
    for line in input_file:
        line = line.strip().split()
        if len(line) == 0 or line[0][0] != 'v':
            continue
        output_file.write(line[0] + ' ' + line[1] + '\n')


if __name__ == '__main__':
    main()
