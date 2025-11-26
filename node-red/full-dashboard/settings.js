module.exports = {
    uiPort: 1880,
    httpAdminRoot: "/",
    httpNodeRoot: "/",
    userDir: ".",
    flowFile: "flows.json",
    credentialSecret: false,
    editorTheme: {
        page: { titleBar: { title: "GasTrack – T.E. Maxson WWTP" } },
        projects: { enabled: false }
    },
    logging: { console: { level: "info" } }
};
