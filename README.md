## Генерация бенчмарка

Чтобы сгенерировать бенчмарк, необходимо запустить `latency.py` либо `throughput.py` и передать 2 параметра:
1.  сколько бит занимает 1 элемент в векторe `(8, 16, 32, 64)`
2. сколько регистров будет занимать 1 вектор `(1, 2, 4, 8)`

По умолчанию параметры равны `32, 1`.

```
python latency.py 32 2
```

```
python throughput.py 16 2
```
Затем нужно скомпилировать полученные файлы `latency_test_e32_m2.cpp` и `throughput_test_e16_m2.cpp`

```
riscv64-unknown-linux-gnu-g++ -march=rv64gcv -mabi=lp64d latency_test_e32_m2.cpp
```

```
riscv64-unknown-linux-gnu-g++ -march=rv64gcv -mabi=lp64d throughput_test_e16_m2.cpp
```
Далее нужно запустить скомпилированные файлы, и результаты измерений будут в `latency_test_e32_m2.csv` и `throughput_test_e16_m2.csv`
