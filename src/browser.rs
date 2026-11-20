//! Internal embedded browser window for Opera GX Store Hub and web stores.
//! Runs in a dedicated child process (`redspotfy --browser <url> <title>`)
//! to avoid event-loop conflicts between winit/eframe and tao/wry.

use std::path::PathBuf;

use tao::event::{Event, WindowEvent};
use tao::event_loop::{ControlFlow, EventLoopBuilder};
use tao::window::WindowBuilder;
use wry::{WebContext, WebViewBuilder};

pub const FLAG: &str = "--browser";

/// Spawn the store or website in the integrated YTM GX Browser child window.
pub fn open_store(url: &str, title: &str) {
    if let Ok(exe) = std::env::current_exe() {
        let mut cmd = std::process::Command::new(exe);
        crate::login::webkit_env(&mut cmd);
        cmd.arg(FLAG)
            .arg(url)
            .arg(title)
            .stdin(std::process::Stdio::null())
            .stderr(std::process::Stdio::null());
        let _ = cmd.spawn();
    }
}

/// Child process entry point for `--browser <url> <title>`.
pub fn child_main(url: &str, title: &str) {
    let data_dir = directories::ProjectDirs::from("", "", "redspotfy")
        .map(|p| p.data_dir().to_path_buf())
        .unwrap_or_else(|| PathBuf::from("."));
    let profile_dir = data_dir.join("gx_browser_profile");
    let _ = std::fs::create_dir_all(&profile_dir);

    let event_loop = EventLoopBuilder::new().build();

    let window = match WindowBuilder::new()
        .with_title(format!("{title} · YTM GX Browser"))
        .with_inner_size(tao::dpi::LogicalSize::new(1280.0, 820.0))
        .build(&event_loop)
    {
        Ok(w) => w,
        Err(e) => {
            log::error!("failed to create browser window: {e}");
            return;
        }
    };

    let mut context = WebContext::new(Some(profile_dir));
    let builder = WebViewBuilder::new_with_web_context(&mut context).with_url(url);

    #[cfg(target_os = "linux")]
    let webview = {
        use tao::platform::unix::WindowExtUnix;
        use wry::WebViewBuilderExtUnix;
        builder.build_gtk(window.default_vbox().expect("tao vbox"))
    };

    #[cfg(not(target_os = "linux"))]
    let webview = builder.build(&window);

    let _webview = match webview {
        Ok(v) => v,
        Err(e) => {
            log::error!("failed to initialize webview: {e}");
            return;
        }
    };

    event_loop.run(move |event, _, flow| {
        *flow = ControlFlow::Wait;
        if let Event::WindowEvent { event: WindowEvent::CloseRequested, .. } = event {
            *flow = ControlFlow::Exit;
        }
    });
}
