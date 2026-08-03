# Electron / desktop-chrome specific pitfalls

These don't show up in web-only design guides because they're specific to native
window chrome.

## Native background color bleeds at theme boundaries

The native `BrowserWindow` background color paints before your app's own CSS
does, and is what's visible at rounded window corners and any custom
traffic-light inset area before/during paint. A hardcoded dark background value
will show as a stray dark sliver at the window edges the instant the app is in
light mode.

**Fix**: sync this value to the app's actual resolved theme via IPC
(`webContents` → main process) whenever the theme changes, don't hardcode it once
at window creation. Concretely:

```ts
// main process
ipcMain.on('theme:sync', (_event, isDark: boolean) => {
  mainWindow?.setBackgroundColor(isDark ? DARK_BG : LIGHT_BG);
});
```

```ts
// renderer, called every time the app resolves its theme (including on initial
// load, not just on user toggle)
window.electronAPI?.syncTheme?.(isDarkResolved);
```

Set the `BrowserWindow` constructor's initial `backgroundColor` to the app's
*primary/default* theme (whichever one is actually the default), not an
arbitrary placeholder — the IPC sync corrects it shortly after first paint, but
the initial value is still what's visible for that first frame.

## Traffic-light positioning must match the real header height

`titleBarStyle: 'hiddenInset'` with a custom `trafficLightPosition` needs to be
vertically centered against the *actual* rendered header row height, not
guessed — recompute if the header's height ever changes, or the traffic lights
visibly float off-center. The formula is simply
`(headerHeightPx - trafficLightClusterHeightPx) / 2` for the y offset; don't
carry forward a value tuned for a different header height after a redesign.

## Theme sync isn't automatic

Test both light and dark OS appearance explicitly — Electron doesn't reliably
inherit a web app's own in-app theme toggle into its native chrome unless you
wire that sync yourself (see above). An app that supports `system` / `dark` /
`light` as independent modes (not just following the OS) needs the sync to fire
on every mode change, not only once at launch.
