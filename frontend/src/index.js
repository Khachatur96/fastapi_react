import React from 'react';
import ReactDOM from 'react-dom/client';
import "bulma/css/bulma.min.css"
import App from './App';

import {UserProvider} from "./context/UserContext";

const container = document.getElementById('root');
const root = ReactDOM.createRoot(container);
root.render(<UserProvider><App name="Saeloun blog" callback={() => console.log("Blog rendered")}/> </UserProvider>);