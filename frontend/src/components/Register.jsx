import React, {useContext, useState} from "react";

import {UserContext} from "../context/UserContext";
import ErrorMessage from "./ErrorMessage";

const Register = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmatopnPassword, setConfirmatopnPassword] = useState("");
    const [errorMessage, seteErrorMessage] = useState("");
    const [, setToken] = useContext(UserContext);

    const submitRegistration = async () => {
        const requestOption = {
            method: "POST",
            headers: {
                "content-type": "application/json"
            },
            body: JSON.stringify({email: email, hashed_password: password}),
        };

        const response = await fetch("/api/users", requestOption);
        const data = await response.json()

        if (!response.ok) {
            seteErrorMessage(data.detail);
        } else {

            setToken(data.access_token);
        }
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (password === confirmatopnPassword && password.length > 5) {
            submitRegistration();
        } else {
            seteErrorMessage("Ensure that the passwords match and greater than 5 characters");
        }

    }

    return (
        <div className="column">
            <form className="box" onSubmit={handleSubmit}>
                <h1 className="title has-text-centered">Register</h1>
                <div className="field">
                    <label className="label">Email Address</label>
                    <div className="control">
                        <input type="email" placeholder="Enter mail " value={email}
                               onChange={(e) => setEmail(e.target.value)}
                               className="input" required/>
                    </div>
                </div>

                <div className="field">
                    <label className="label">Password</label>
                    <div className="control">
                        <input type="password" placeholder="Enter a password " value={password}
                               onChange={(e) => setPassword(e.target.value)}
                               className="input" required/>
                    </div>
                </div>

                <div className="field">
                    <label className="label">Confirm password</label>
                    <div className="control">
                        <input type="password" placeholder="Confirm password" value={confirmatopnPassword}
                               onChange={(e) => setConfirmatopnPassword(e.target.value)}
                               className="input" required/>
                    </div>
                </div>
                <ErrorMessage message={errorMessage}/>
                <br/>
                <button className="button is-primary" type="submit">Register

                </button>

            </form>
        </div>
    );


};

export default Register;