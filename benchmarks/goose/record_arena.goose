struct Record {
    id: i64,
    val: i64,
    payload: u8[varint]
}

fn process_records(n: i64, prng_seed: u32) -> u32 {
    var state = prng_seed;
    var records: Record[>..] = [];
    var i: i64 = 0;
    while i < n {
        state = state * 1664525 + 1013904223;
        let len = 16 + (state % 32) as i64;
        var p: u8[>..] = [];
        var k: i64 = 0;
        while k < len {
            state = state * 1664525 + 1013904223;
            p.push((state >> 24) as u8);
            k++;
        }
        state = state * 1664525 + 1013904223;
        let v = (state >> 16) as i64;
        records.push(Record { id: i, val: v, payload: copy(p) });
        i++;
    }

    var sum: u32 = 0;
    for r in records {
        sum += r.id as u32;
        sum += r.val as u32;
        sum += r.payload.len as u32;
        for b in r.payload {
            sum = (sum * 31) + b;
        }
    }
    return sum;
}

fn record_arena_step(n: i64, inner: i64) -> u32 {
    var check: u32 = 0;
    var j: i64 = 0;
    while j < inner {
        check ^= process_records(n, 0x12345678 + j as u32);
        j++;
    }
    return check;
}

fn main() {
    let check = record_arena_step(64, 50);
    print("record_arena check: ", check, "\n");
}
