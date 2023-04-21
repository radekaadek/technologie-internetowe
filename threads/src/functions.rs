use rand::Rng;
use std::os::unix::net::UnixDatagram;
use std::path::Path;

pub fn connect(path: &str) -> UnixDatagram {
    let socket = UnixDatagram::unbound().unwrap();
    match socket.connect(path) {
        Ok(socket) => socket,
        Err(e) => {
            println!("Couldn't connect: {:?}", e);
            return socket;
        }
    };
    socket
}

pub fn send_msg(socket: &UnixDatagram, msg: &str) {
    socket.send(msg.as_bytes()).expect("recv function failed");
}

fn unlink_socket(path: impl AsRef<Path>) {
    let path = path.as_ref();
    if Path::new(path).exists() {
        let result = std::fs::remove_file(path);
        match result {
            Err(e) => {
                println!("Couldn't remove the file: {:?}", e);
            }
            _ => {}
        }
    }
}

pub fn client1(msg: &str) -> std::thread::JoinHandle<()> {
    let owned_msg = msg.to_owned();
    let client_thread = std::thread::spawn(move || {
        let mut rng = rand::thread_rng();
        pub static FILE_PATH: &'static str = "/tmp/datagram2.sock";
        let socket = connect(FILE_PATH);
        loop {
            send_msg(&socket, &owned_msg);
            let milis = rng.gen_range(1000..2000);
            std::thread::sleep(std::time::Duration::from_millis(milis));
        }
    });
    client_thread
}

pub fn client2(msg: &str) -> std::thread::JoinHandle<()> {
    let owned_msg = msg.to_owned();
    let client_thread = std::thread::spawn(move || {
        let mut rng = rand::thread_rng();
        pub static FILE_PATH: &'static str = "/tmp/datagram1.sock";
        let socket = connect(FILE_PATH);
        loop {
            send_msg(&socket, &owned_msg);
            let milis = rng.gen_range(1000..5000);
            std::thread::sleep(std::time::Duration::from_millis(milis));
        }
    });
    client_thread
}

pub fn server1(name: &str) -> std::thread::JoinHandle<()> {
    let owned_name = name.to_owned();
    let server_thread = std::thread::spawn(move || {
        pub static FILE_PATH: &'static str = "/tmp/datagram1.sock";
        let mut buf = vec![0; 1024];
        unlink_socket(FILE_PATH);
        let socket = match UnixDatagram::bind(FILE_PATH) {
            Ok(socket) => socket,
            Err(e) => {
                println!("Couldn't bind: {:?}", e);
                return;
            }
        };
        println!("Waiting for client to connect to {}...", owned_name);
        loop {
            socket
                .recv(buf.as_mut_slice())
                .expect("recv function failed");
            match std::str::from_utf8(buf.as_slice()) {
                Ok(v) => {
                    let v = v.trim_matches(char::from(0));
                    println!("{} received: {:?}", owned_name, v);
                    // send back to client
                }
                Err(e) => println!("Invalid UTF-8 sequence: {}", e),
            }
        }
    });
    server_thread
}

pub fn server2(name: &str) -> std::thread::JoinHandle<()> {
    let owned_name = name.to_owned();
    let server_thread = std::thread::spawn(move || {
        pub static FILE_PATH: &'static str = "/tmp/datagram2.sock";
        let mut buf = vec![0; 1024];
        unlink_socket(FILE_PATH);
        let socket = match UnixDatagram::bind(FILE_PATH) {
            Ok(socket) => socket,
            Err(e) => {
                println!("Couldn't bind: {:?}", e);
                return;
            }
        };
        println!("Waiting for client to connect to {}...", owned_name);
        loop {
            socket
                .recv(buf.as_mut_slice())
                .expect("recv function failed");
            match std::str::from_utf8(buf.as_slice()) {
                Ok(v) => {
                    let v = v.trim_matches(char::from(0));
                    println!("{} received: {:?}", owned_name, v);
                    // send back to client
                }
                Err(e) => println!("Invalid UTF-8 sequence: {}", e),
            }
        }
    });
    server_thread
}
