use crate::functions::server1;
use crate::functions::server2;
use std::thread;

pub fn servers() -> (thread::JoinHandle<()>, thread::JoinHandle<()>) {
    let serv1 = server1("Program 1 server");
    let serv2 = server2("Program 2 server");
    (serv1, serv2)
}
