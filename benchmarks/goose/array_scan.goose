let N = 1024;
var values: u32[1024] = [0; 1024];

fn init_data() {
    var state: u32 = 0x12345678;
    var i = 0;
    while i < N {
        state = state * 1664525 + 1013904223;
        values[i] = state;
        i++;
    }
}

fn array_scan() -> u32 {
    var sum: u32 = 0;
    var i = 0;
    while i < N {
        sum += values[i] >> 16;
        i++;
    }
    return sum;
}

fn goose_benchmark_step(inner: i32) -> u32 {
    var check: u32 = 0;
    var j = 0;
    while j < inner {
        check ^= array_scan();
        j++;
    }
    return check;
}

fn main() {
    init_data();
    let expected = array_scan();
    let result = goose_benchmark_step(1000);
    print("expected: ", expected, " result: ", result, "\n");
}
