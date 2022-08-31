import "./App.css";
import { useState } from "react";
import { Overlay } from "./components/Overlay";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { MuiTable } from "./components/MuiTable";
import { DataDisplay } from "./components/DataDisplay";
import { TextWall } from "./components/TextWall";
import { TestPage } from "./components/TestPage";
// import { Login } from "./components/Login";
// import useToken from "./components/useToken";

// function setToken(userToken) {
//   sessionStorage.setItem("token", JSON.stringify(userToken));
// }

// function getToken() {
//   const tokenString = sessionStorage.getItem("token");
//   const userToken = JSON.parse(tokenString);
//   return userToken?.token;
// }

function App() {
  // const [token, setToken] = useState();

  // if (!token) {
  //   return <Login setToken={setToken} />;
  // }

  const logout = () => {
    // setToken(false);
    // sessionStorage.clear();
  };

  return (
    <BrowserRouter>
      <div className="App">
        <Overlay logout={logout}>
          <Routes>
            <Route path="/" element={<Navigate to="/status" />} />
            <Route path="/status" element={<MuiTable />} />
            <Route path="/data" element={<DataDisplay />} />
            <Route path="/text" element={<TextWall />} />
            <Route path="/test" element={<TestPage />} />
            <Route
              path="*"
              element={
                <main style={{ padding: "1rem" }}>
                  <p>There's nothing here!</p>
                </main>
              }
            />
          </Routes>
        </Overlay>
      </div>
    </BrowserRouter>

    // <div className="App">
    //   <Overlay>{props.children}</Overlay>
    // </div>
  );
}

export default App;
