// A program that creates 100 files in the current directory
// and then deletes them.

use std::fs::File;
use std::io::prelude::*;
use std::iter;
use std::path::Path;

fn main() {
    let number_of_files = 100;
    let mut threads: Vec<std::thread::JoinHandle<()>> = Vec::new();
    for i in 1..number_of_files + 1 {
        let nowy = std::thread::spawn(move || {
            let file_name = format!("file{}", i);
            let path = Path::new(&file_name);
            let mut file = match File::create(&path) {
                Err(why) => panic!("couldn't create {}: {}", path.display(), why),
                Ok(file) => file,
            };
            let repeated: String = iter::repeat("Hello World!").take(1000000).collect();

            if let Err(why) = file.write_all(repeated.as_bytes()) {
                panic!("couldn't write to {}: {}", path.display(), why);
            }
        });
        threads.push(nowy);
    }
    // Sync
    for thread in threads {
        thread.join().unwrap();
    }
    let mut delete_threads: Vec<std::thread::JoinHandle<()>> = Vec::new();
    // Delete files
    for i in 1..number_of_files + 1 {
        let nowy = std::thread::spawn(move || {
            let file_name = format!("file{}", i);
            let path = Path::new(&file_name);
            if path.exists() {
                let result = std::fs::remove_file(path);
                match result {
                    Err(e) => {
                        println!("Couldn't remove the file: {:?}", e);
                    }
                    _ => {}
                }
            }
        });
        delete_threads.push(nowy);
    }
    // Sync
    for thread in delete_threads {
        thread.join().unwrap();
    }
}