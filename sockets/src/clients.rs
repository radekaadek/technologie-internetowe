use crate::functions::{client1, client2};
use std::thread;

pub fn clients() -> (thread::JoinHandle<()>, thread::JoinHandle<()>) {
    let client1 = client1("Message from program 1");
    let client2 = client2("Message from program 2");
    (client1, client2)
}
