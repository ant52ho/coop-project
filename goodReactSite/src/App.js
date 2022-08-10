import "./App.css";
import { Overlay } from "./components/Overlay";

function App(props) {
  return (
    <div className="App">
      <Overlay>{props.children}</Overlay>
    </div>
  );
}

export default App;
