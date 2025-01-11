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
├── .angular                               # files required to build the Angular app
├── .e2e                                   # files used to test the app
├── BUILD.bazel
├── README.md
├── angular.json                           # describes the Angular app to the app building tools
├── config.json
├── idx
│   └── dev.nix
├── package-lock.json
├── package.json                           # used by npm (the node package manager) to run the finished app
├── package.json.template
├── src
│   ├── app
│   │   ├── app.component.css              # style sheet for this component
│   │   ├── app.component.ts               # source file that describes the app-root component. This is the top-level Angular component in the app
│   │   └── app.config.ts
│   ├── assets                             # contains images used by the app
│   │   ├── angular.svg
│   │   ├── location-pin.svg
│   │   └── logo.svg
│   ├── favicon.ico
│   ├── index.html                         # app's top level HTML template
│   ├── main.ts                            # where the app starts running
│   └── styles.css                         # app's top level style sheet
└── tsconfig.*                             # files that describe the app's configuration to the TypeScript compiler
```

**Angular Components**

Angular apps are built around components, which are Angular's building blocks. Components contain the code, HTML layout, and CSS style information that provide the function and appearance of an element in the app. In Angular, components can contain other components. An app's functions and appearance can be divided and partitioned into components.

In Angular, components have metadata that define its properties. When you create your `HomeComponent`, you use these properties:

- `selector`: to describe how Angular refers to the component in templates.
- `standalone`: to describe whether the component requires a NgModule.
- `imports`: to describe the component's dependencies.
- `template`: to describe the component's HTML markup and layout.
- `styleUrls`: to list the URLs of the CSS files that the component uses in an array.

**Creating a Component**

```shell
ng generate component home
```
