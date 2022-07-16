import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";
import AppTest from "./AppTest";
import reportWebVitals from "./reportWebVitals";

// new code
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MuiTable } from "./components/MuiTable";
import { MuiDrawer } from "./components/MuiDrawer";
import { DataDisplay } from "./components/DataDisplay";
import { TextWall } from "./components/TextWall";
import { Test } from "./components/Test";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter>
    <App>
      <Routes>
        <Route path="/" element={<Navigate to="/status" />} />
        <Route path="/status" element={<MuiTable />} />
        <Route path="/data" element={<DataDisplay />} />
        <Route path="/text" element={<TextWall />} />
        <Route path="/test" element={<Test />} />
        <Route
          path="*"
          element={
            <main style={{ padding: "1rem" }}>
              <p>There's nothing here!</p>
            </main>
          }
        />
      </Routes>
      {/* <Routes>
      <Route path="/" element={<AppTest />}>
        <Route path="invoices" element={<Invoices />}>
          <Route
            index
            element={
              <main style={{ padding: "1rem" }}>
                <p>Select an invoice</p>
              </main>
            }
          />
          <Route path=":invoiceId" element={<Invoice />} />
        </Route>

        <Route path="expenses" element={<Expenses />} />
        <Route
          path="*"
          element={
            <main style={{ padding: "1rem" }}>
              <p>There's nothing here!</p>
            </main>
          }
        />
      </Route>
    </Routes> */}
      {/* <AppTest /> */}
    </App>
  </BrowserRouter>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
