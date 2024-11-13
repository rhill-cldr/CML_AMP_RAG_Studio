/* eslint-disable */

// @ts-nocheck

// noinspection JSUnusedGlobalSymbols

// This file was automatically generated by TanStack Router.
// You should NOT make any changes in this file as it will be overwritten.
// Additionally, you should also exclude this file from your linter and/or formatter to prevent it from being checked or modified.

import { createFileRoute } from '@tanstack/react-router'

// Import Routes

import { Route as rootRoute } from './routes/__root'
import { Route as LayoutImport } from './routes/_layout'
import { Route as IndexImport } from './routes/index'
import { Route as LayoutSessionsIndexImport } from './routes/_layout/sessions/index'
import { Route as LayoutSessionsSessionIdImport } from './routes/_layout/sessions/$sessionId'
import { Route as LayoutDataLayoutDatasourcesImport } from './routes/_layout/data/_layout-datasources'
import { Route as LayoutDataLayoutDatasourcesIndexImport } from './routes/_layout/data/_layout-datasources/index'
import { Route as LayoutDataLayoutDatasourcesDataSourceIdImport } from './routes/_layout/data/_layout-datasources/$dataSourceId'

// Create Virtual Routes

const LayoutDataImport = createFileRoute('/_layout/data')()

// Create/Update Routes

const LayoutRoute = LayoutImport.update({
  id: '/_layout',
  getParentRoute: () => rootRoute,
} as any).lazy(() => import('./routes/_layout.lazy').then((d) => d.Route))

const IndexRoute = IndexImport.update({
  id: '/',
  path: '/',
  getParentRoute: () => rootRoute,
} as any).lazy(() => import('./routes/index.lazy').then((d) => d.Route))

const LayoutDataRoute = LayoutDataImport.update({
  id: '/data',
  path: '/data',
  getParentRoute: () => LayoutRoute,
} as any)

const LayoutSessionsIndexRoute = LayoutSessionsIndexImport.update({
  id: '/sessions/',
  path: '/sessions/',
  getParentRoute: () => LayoutRoute,
} as any).lazy(() =>
  import('./routes/_layout/sessions/index.lazy').then((d) => d.Route),
)

const LayoutSessionsSessionIdRoute = LayoutSessionsSessionIdImport.update({
  id: '/sessions/$sessionId',
  path: '/sessions/$sessionId',
  getParentRoute: () => LayoutRoute,
} as any).lazy(() =>
  import('./routes/_layout/sessions/$sessionId.lazy').then((d) => d.Route),
)

const LayoutDataLayoutDatasourcesRoute =
  LayoutDataLayoutDatasourcesImport.update({
    id: '/_layout-datasources',
    getParentRoute: () => LayoutDataRoute,
  } as any)

const LayoutDataLayoutDatasourcesIndexRoute =
  LayoutDataLayoutDatasourcesIndexImport.update({
    id: '/',
    path: '/',
    getParentRoute: () => LayoutDataLayoutDatasourcesRoute,
  } as any).lazy(() =>
    import('./routes/_layout/data/_layout-datasources/index.lazy').then(
      (d) => d.Route,
    ),
  )

const LayoutDataLayoutDatasourcesDataSourceIdRoute =
  LayoutDataLayoutDatasourcesDataSourceIdImport.update({
    id: '/$dataSourceId',
    path: '/$dataSourceId',
    getParentRoute: () => LayoutDataLayoutDatasourcesRoute,
  } as any).lazy(() =>
    import('./routes/_layout/data/_layout-datasources/$dataSourceId.lazy').then(
      (d) => d.Route,
    ),
  )

// Populate the FileRoutesByPath interface

declare module '@tanstack/react-router' {
  interface FileRoutesByPath {
    '/': {
      id: '/'
      path: '/'
      fullPath: '/'
      preLoaderRoute: typeof IndexImport
      parentRoute: typeof rootRoute
    }
    '/_layout': {
      id: '/_layout'
      path: ''
      fullPath: ''
      preLoaderRoute: typeof LayoutImport
      parentRoute: typeof rootRoute
    }
    '/_layout/data': {
      id: '/_layout/data'
      path: '/data'
      fullPath: '/data'
      preLoaderRoute: typeof LayoutDataImport
      parentRoute: typeof LayoutImport
    }
    '/_layout/data/_layout-datasources': {
      id: '/_layout/data/_layout-datasources'
      path: '/data'
      fullPath: '/data'
      preLoaderRoute: typeof LayoutDataLayoutDatasourcesImport
      parentRoute: typeof LayoutDataRoute
    }
    '/_layout/sessions/$sessionId': {
      id: '/_layout/sessions/$sessionId'
      path: '/sessions/$sessionId'
      fullPath: '/sessions/$sessionId'
      preLoaderRoute: typeof LayoutSessionsSessionIdImport
      parentRoute: typeof LayoutImport
    }
    '/_layout/sessions/': {
      id: '/_layout/sessions/'
      path: '/sessions'
      fullPath: '/sessions'
      preLoaderRoute: typeof LayoutSessionsIndexImport
      parentRoute: typeof LayoutImport
    }
    '/_layout/data/_layout-datasources/$dataSourceId': {
      id: '/_layout/data/_layout-datasources/$dataSourceId'
      path: '/$dataSourceId'
      fullPath: '/data/$dataSourceId'
      preLoaderRoute: typeof LayoutDataLayoutDatasourcesDataSourceIdImport
      parentRoute: typeof LayoutDataLayoutDatasourcesImport
    }
    '/_layout/data/_layout-datasources/': {
      id: '/_layout/data/_layout-datasources/'
      path: '/'
      fullPath: '/data/'
      preLoaderRoute: typeof LayoutDataLayoutDatasourcesIndexImport
      parentRoute: typeof LayoutDataLayoutDatasourcesImport
    }
  }
}

// Create and export the route tree

interface LayoutDataLayoutDatasourcesRouteChildren {
  LayoutDataLayoutDatasourcesDataSourceIdRoute: typeof LayoutDataLayoutDatasourcesDataSourceIdRoute
  LayoutDataLayoutDatasourcesIndexRoute: typeof LayoutDataLayoutDatasourcesIndexRoute
}

const LayoutDataLayoutDatasourcesRouteChildren: LayoutDataLayoutDatasourcesRouteChildren =
  {
    LayoutDataLayoutDatasourcesDataSourceIdRoute:
      LayoutDataLayoutDatasourcesDataSourceIdRoute,
    LayoutDataLayoutDatasourcesIndexRoute:
      LayoutDataLayoutDatasourcesIndexRoute,
  }

const LayoutDataLayoutDatasourcesRouteWithChildren =
  LayoutDataLayoutDatasourcesRoute._addFileChildren(
    LayoutDataLayoutDatasourcesRouteChildren,
  )

interface LayoutDataRouteChildren {
  LayoutDataLayoutDatasourcesRoute: typeof LayoutDataLayoutDatasourcesRouteWithChildren
}

const LayoutDataRouteChildren: LayoutDataRouteChildren = {
  LayoutDataLayoutDatasourcesRoute:
    LayoutDataLayoutDatasourcesRouteWithChildren,
}

const LayoutDataRouteWithChildren = LayoutDataRoute._addFileChildren(
  LayoutDataRouteChildren,
)

interface LayoutRouteChildren {
  LayoutDataRoute: typeof LayoutDataRouteWithChildren
  LayoutSessionsSessionIdRoute: typeof LayoutSessionsSessionIdRoute
  LayoutSessionsIndexRoute: typeof LayoutSessionsIndexRoute
}

const LayoutRouteChildren: LayoutRouteChildren = {
  LayoutDataRoute: LayoutDataRouteWithChildren,
  LayoutSessionsSessionIdRoute: LayoutSessionsSessionIdRoute,
  LayoutSessionsIndexRoute: LayoutSessionsIndexRoute,
}

const LayoutRouteWithChildren =
  LayoutRoute._addFileChildren(LayoutRouteChildren)

export interface FileRoutesByFullPath {
  '/': typeof IndexRoute
  '': typeof LayoutRouteWithChildren
  '/data': typeof LayoutDataLayoutDatasourcesRouteWithChildren
  '/sessions/$sessionId': typeof LayoutSessionsSessionIdRoute
  '/sessions': typeof LayoutSessionsIndexRoute
  '/data/$dataSourceId': typeof LayoutDataLayoutDatasourcesDataSourceIdRoute
  '/data/': typeof LayoutDataLayoutDatasourcesIndexRoute
}

export interface FileRoutesByTo {
  '/': typeof IndexRoute
  '': typeof LayoutRouteWithChildren
  '/data': typeof LayoutDataLayoutDatasourcesIndexRoute
  '/sessions/$sessionId': typeof LayoutSessionsSessionIdRoute
  '/sessions': typeof LayoutSessionsIndexRoute
  '/data/$dataSourceId': typeof LayoutDataLayoutDatasourcesDataSourceIdRoute
}

export interface FileRoutesById {
  __root__: typeof rootRoute
  '/': typeof IndexRoute
  '/_layout': typeof LayoutRouteWithChildren
  '/_layout/data': typeof LayoutDataRouteWithChildren
  '/_layout/data/_layout-datasources': typeof LayoutDataLayoutDatasourcesRouteWithChildren
  '/_layout/sessions/$sessionId': typeof LayoutSessionsSessionIdRoute
  '/_layout/sessions/': typeof LayoutSessionsIndexRoute
  '/_layout/data/_layout-datasources/$dataSourceId': typeof LayoutDataLayoutDatasourcesDataSourceIdRoute
  '/_layout/data/_layout-datasources/': typeof LayoutDataLayoutDatasourcesIndexRoute
}

export interface FileRouteTypes {
  fileRoutesByFullPath: FileRoutesByFullPath
  fullPaths:
    | '/'
    | ''
    | '/data'
    | '/sessions/$sessionId'
    | '/sessions'
    | '/data/$dataSourceId'
    | '/data/'
  fileRoutesByTo: FileRoutesByTo
  to:
    | '/'
    | ''
    | '/data'
    | '/sessions/$sessionId'
    | '/sessions'
    | '/data/$dataSourceId'
  id:
    | '__root__'
    | '/'
    | '/_layout'
    | '/_layout/data'
    | '/_layout/data/_layout-datasources'
    | '/_layout/sessions/$sessionId'
    | '/_layout/sessions/'
    | '/_layout/data/_layout-datasources/$dataSourceId'
    | '/_layout/data/_layout-datasources/'
  fileRoutesById: FileRoutesById
}

export interface RootRouteChildren {
  IndexRoute: typeof IndexRoute
  LayoutRoute: typeof LayoutRouteWithChildren
}

const rootRouteChildren: RootRouteChildren = {
  IndexRoute: IndexRoute,
  LayoutRoute: LayoutRouteWithChildren,
}

export const routeTree = rootRoute
  ._addFileChildren(rootRouteChildren)
  ._addFileTypes<FileRouteTypes>()

/* ROUTE_MANIFEST_START
{
  "routes": {
    "__root__": {
      "filePath": "__root.tsx",
      "children": [
        "/",
        "/_layout"
      ]
    },
    "/": {
      "filePath": "index.tsx"
    },
    "/_layout": {
      "filePath": "_layout.tsx",
      "children": [
        "/_layout/data",
        "/_layout/sessions/$sessionId",
        "/_layout/sessions/"
      ]
    },
    "/_layout/data": {
      "filePath": "_layout/data",
      "parent": "/_layout",
      "children": [
        "/_layout/data/_layout-datasources"
      ]
    },
    "/_layout/data/_layout-datasources": {
      "filePath": "_layout/data/_layout-datasources.tsx",
      "parent": "/_layout/data",
      "children": [
        "/_layout/data/_layout-datasources/$dataSourceId",
        "/_layout/data/_layout-datasources/"
      ]
    },
    "/_layout/sessions/$sessionId": {
      "filePath": "_layout/sessions/$sessionId.tsx",
      "parent": "/_layout"
    },
    "/_layout/sessions/": {
      "filePath": "_layout/sessions/index.tsx",
      "parent": "/_layout"
    },
    "/_layout/data/_layout-datasources/$dataSourceId": {
      "filePath": "_layout/data/_layout-datasources/$dataSourceId.tsx",
      "parent": "/_layout/data/_layout-datasources"
    },
    "/_layout/data/_layout-datasources/": {
      "filePath": "_layout/data/_layout-datasources/index.tsx",
      "parent": "/_layout/data/_layout-datasources"
    }
  }
}
ROUTE_MANIFEST_END */
