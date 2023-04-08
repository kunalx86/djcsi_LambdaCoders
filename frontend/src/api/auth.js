import axios from "axios";
const URL = "http://localhost:8080";

export const signUp = async (data) => {
    return await axios.post(URL + "/parent/signUp", data)
}

export const signIn = async (data) => {
    return await axios.post(URL + "/parent/signIn", data);
}