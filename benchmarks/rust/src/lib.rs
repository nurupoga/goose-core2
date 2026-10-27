#![no_std]

use core::hint::black_box;
use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

const N: usize = 1024;
static mut VALUES: [u32; N] = [0; N];

#[no_mangle]
pub extern "C" fn rust_bench_init() {
    let mut state: u32 = 0x12345678;
    unsafe {
        for i in 0..N {
            state = state.wrapping_mul(1664525).wrapping_add(1013904223);
            VALUES[i] = state;
        }
    }
}

#[inline(never)]
#[no_mangle]
pub extern "C" fn rust_array_scan() -> u32 {
    let mut sum: u32 = 0;
    unsafe {
        for &v in VALUES.iter() {
            sum = sum.wrapping_add(v >> 16);
        }
    }
    sum
}

#[inline(never)]
#[no_mangle]
pub extern "C" fn rust_array_scan_step(inner: i32) -> u32 {
    let mut check: u32 = 0;
    for _ in 0..inner {
        check ^= black_box(rust_array_scan());
    }
    check
}

static mut ARENA_BUF: [u8; 64 * 64] = [0; 64 * 64];

#[no_mangle]
pub extern "C" fn rust_record_arena_step(n: i64, inner: i64) -> u32 {
    let mut check: u32 = 0;
    let n = n as usize;
    for j in 0..inner {
        let mut state = (0x12345678u32).wrapping_add(j as u32);
        let mut offset = 0;
        let mut sum: u32 = 0;

        for i in 0..n {
            state = state.wrapping_mul(1664525).wrapping_add(1013904223);
            let len = 16 + (state % 32) as usize;
            let start = offset;
            let end = offset + len;
            offset = end;

            unsafe {
                for k in start..end {
                    state = state.wrapping_mul(1664525).wrapping_add(1013904223);
                    ARENA_BUF[k] = (state >> 24) as u8;
                }
                state = state.wrapping_mul(1664525).wrapping_add(1013904223);
                let v = (state >> 16) as i64;

                sum = sum.wrapping_add(i as u32);
                sum = sum.wrapping_add(v as u32);
                sum = sum.wrapping_add(len as u32);
                for &b in &ARENA_BUF[start..end] {
                    sum = sum.wrapping_mul(31).wrapping_add(b as u32);
                }
            }
        }
        check ^= sum;
    }
    check
}
