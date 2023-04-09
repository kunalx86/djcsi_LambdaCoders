import axios from "axios";
const API = axios.create({ baseURL: "http://localhost:8080" })


API.interceptors.request.use((req) => {
    if (localStorage.getItem('profile')) {
        req.headers.authorization = `Bearer ${JSON.parse(localStorage.getItem('profile')).token}`;
    }
    return req;
});


export const getChildrens = async (userId) => {
    return await API.get(`/parent/getChildrens/${userId}`);
}

export const addChildren = async (data) => {
    return await API.post(`/parent/addChildren`, data);
}

export const getChildren = async (childId) => {
    return await API.get(`/parent/getChildren/${childId}`);
}

export const updateChildren = async (childId, data) => {
    return await API.post(`/parent/updateChildren/${childId}`, data);
}

export const getVisits = async (userId) => {
    return await API.get(`/parent/getVisits/${userId}`);
}