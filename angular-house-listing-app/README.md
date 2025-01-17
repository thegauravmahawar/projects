# House Listing Application

## Reference

- [Angular First App](https://angular.dev/tutorials/first-app)

## Local setup

**Install Angular**

```shell
npm install -g @angular/cli
```

**Install dependencies**

```shell
npm install
```

**Build and serve the application**

```shell
ng serve
```

## Project structure

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

## Components

Angular apps are built around components, which are Angular's building blocks. Components contain the code, HTML layout, and CSS style information that provide the function and appearance of an element in the app. In Angular, components can contain other components. An app's functions and appearance can be divided and partitioned into components.

In Angular, components have metadata that define its properties. When you create your component, you use these properties:

- `selector`: to describe how Angular refers to the component in templates.
- `standalone`: to describe whether the component requires a NgModule.
- `imports`: to describe the component's dependencies.
- `template`: to describe the component's HTML markup and layout.
- `styleUrls`: to list the URLs of the CSS files that the component uses in an array.

**Creating a Component**

```shell
ng generate component home
```

## Interfaces

`Interfaces` are custom data types for your app.

Angular uses TypeScript to take advantage of working in a strongly typed programming environment. Strong type checking reduces the likelihood of one element in your app sending incorrectly formatted data to another.

## Inputs

`Inputs` allow components to share data. The direction of the data sharing is from parent component to child component.

## Services

Angular services provide a way for you to separate Angular app data and functions that can be used by multiple components in your app. To be used by multiple components, a service must be made injectable. Services that are injectable and used by a component become dependencies of that component. The component depends on those services and can't function without them.

## Routing

The Angular Router enables users to declare routes and specify which component should be displayed on the screen if that route is requested by the application.

Route parameters enable you to include dynamic information as a part of your route URL.

The `routerLink` directive enables Angular's router to create dynamic links in the application. The value assigned to the `routerLink` is an array with two entries: the static portion of the path and the dynamic data.

For the `routerLink` to work in the template, add a file level import of `RouterLink` and `RouterOutlet` from '@angular/router', then update the component `imports` array to include both `RouterLink` and `RouterOutlet`.
