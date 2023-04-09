import { useState, useEffect } from "react";
import { getVisits } from "api/parent";
function Child() {
    const [user, setUser] = useState(JSON.parse(localStorage.getItem("profile"))?.user)
    const [childs, setChilds] = useState([])

    useEffect(() => {
        setUser(JSON.parse(localStorage.getItem("profile"))?.user)


        async function fetchData() {
            const response = await getVisits(user._id);
            console.log(response.data)
            setChilds(response.data)
        }
        fetchData();

    }, [])

    return childs;
}

export default Child;