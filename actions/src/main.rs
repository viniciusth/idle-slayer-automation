use std::{
    fs::File,
    io::Write,
    path::PathBuf,
    process::exit,
    sync::{Arc, Mutex},
    time::Instant,
};

use winapi::um::winuser;

use clap::Parser;
use inputbot::{handle_input_events, KeybdKey};

/// Search for a pattern in a file and display the lines that contain it.
#[derive(Parser)]
struct Cli {
    /// What to execute
    job: Job,
    /// Output/Input file
    #[clap(short, long)]
    file: PathBuf,
}

#[derive(Parser, Clone)]
enum Job {
    Record,
    Play,
}

impl std::str::FromStr for Job {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "record" => Ok(Job::Record),
            "play" => Ok(Job::Play),
            _ => Err("Invalid job".to_string()),
        }
    }
}

fn main() {
    let args = Cli::parse();

    match args.job {
        Job::Record => {
            record(args.file);
        }
        Job::Play => {
            play(args.file);
        }
    }
}

fn record(output: PathBuf) {
    println!("Waiting for 's' to start recording...");
    let file = Arc::new(Mutex::new(File::create(output).unwrap()));
    let recording = Arc::new(Mutex::new(false));
    let start_time = Arc::new(Mutex::new(None));
    let finished = Arc::new(Mutex::new(false));
    handle_skey(recording.clone(), start_time.clone(), finished.clone());
    handle_space(recording, start_time, file);

    handle_input_events(false);

    fn handle_skey(
        recording: Arc<Mutex<bool>>,
        start_time: Arc<Mutex<Option<std::time::Instant>>>,
        finished: Arc<Mutex<bool>>,
    ) {
        KeybdKey::SKey.bind(move || {
            let mut recording = recording.lock().unwrap();
            *recording = !*recording;
            if *recording {
                let mut start_time = start_time.lock().unwrap();
                println!("Recording started");
                *start_time = Some(std::time::Instant::now());
            } else {
                println!("Recording stopped");
                let mut finished = finished.lock().unwrap();
                *finished = true;
                exit(0);
            }
        });
    }

    fn handle_space(
        recording: Arc<Mutex<bool>>,
        start_time: Arc<Mutex<Option<std::time::Instant>>>,
        file: Arc<Mutex<File>>,
    ) {
        let release_recording = recording.clone();
        let release_start_time = start_time.clone();
        let release_file = file.clone();
        KeybdKey::SpaceKey.bind(move || {
            let recording = recording.lock().unwrap();
            if *recording {
                let start_time = start_time.lock().unwrap();
                if let Some(start_time) = *start_time {
                    let elapsed = start_time.elapsed();
                    println!("+Elapsed: {:?}", elapsed);
                    let mut file = file.lock().unwrap();
                    file.write(format!("+:{}\n", elapsed.as_nanos()).as_bytes())
                        .unwrap();
                }
            }
        });

        KeybdKey::SpaceKey.bind_release(move || {
            let recording = release_recording.lock().unwrap();
            if *recording {
                let start_time = release_start_time.lock().unwrap();
                if let Some(start_time) = *start_time {
                    let elapsed = start_time.elapsed();
                    println!("-Elapsed: {:?}", elapsed);
                    let mut file = release_file.lock().unwrap();
                    file.write(format!("-:{}\n", elapsed.as_nanos()).as_bytes())
                        .unwrap();
                }
            }
        });
    }
}

fn play(file: PathBuf) {
    let file = std::fs::read_to_string(file).unwrap();
    let lines = file.lines();
    let mut last_sign = None;
    let now = Instant::now();

    for line in lines {
        let (sign, time) = line.split_at(1);
        if Some(sign) == last_sign {
            continue;
        }
        let time = time[1..].parse::<u128>().unwrap();
        while now.elapsed().as_nanos() < time {
            continue;
        }
        match sign {
            "+" => unsafe {
                winuser::keybd_event(winuser::VK_SPACE as u8, 0, 0, 0);
            },
            "-" => unsafe {
                winuser::keybd_event(winuser::VK_SPACE as u8, 0, winuser::KEYEVENTF_KEYUP, 0);
            },
            _ => {}
        }
        println!(
            "Delta: {}ms",
            (now.elapsed().as_nanos() - time) as f64 / 1_000_000 as f64
        );
        last_sign = Some(sign);
    }
}
