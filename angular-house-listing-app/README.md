# House Listing Application

**Install dependencies**

```shell
npm install
```

**Build and serve the application**

```shell
ng serve
```

**Project structure**

```bash
.
├── .angular               # files required to build the Angular app
├── .e2e               #  files used to test the app
├── BUILD.bazel
├── README.md
├── angular.json               # describes the Angular app to the app building tools
├── config.json
├── idx
│   └── dev.nix
├── package-lock.json
├── package.json               # used by npm (the node package manager) to run the finished app
├── package.json.template
├── src
│   ├── app
│   │   ├── app.component.css               # style sheet for this component
│   │   ├── app.component.ts               # source file that describes the app-root component. This is the top-level Angular component in the app
│   │   └── app.config.ts
│   ├── assets               # contains images used by the app
│   │   ├── angular.svg
│   │   ├── location-pin.svg
│   │   └── logo.svg
│   ├── favicon.ico
│   ├── index.html               #  app's top level HTML template
│   ├── main.ts               # where the app starts running
│   └── styles.css               # app's top level style sheet
└── tsconfig.*               # files that describe the app's configuration to the TypeScript compiler
```
