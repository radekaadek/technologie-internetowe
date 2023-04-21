pub mod clients;
pub mod functions;
pub mod servers;

use clients::clients;
use servers::servers;

fn main() {
    let servs = servers();
    let progs = clients();
    servs.0.join().unwrap();
    servs.1.join().unwrap();

    progs.0.join().unwrap();
    progs.1.join().unwrap();
}
