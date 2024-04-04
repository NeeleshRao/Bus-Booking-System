import { GoogleGenerativeAI } from "@google/generative-ai";
const conv = new showdown.Converter();

const genAI = new GoogleGenerativeAI("<API key>");
const gen_model = genAI.getGenerativeModel({ model: "gemini-pro" });
const chat = gen_model.startChat({
    generationConfig: {
        maxOutputTokens: 500,
    },
});

const chatGemini = async (message) => {
    addMessage(message, "end");
    let res = await chat.sendMessage(message);
    res = await res.response;
    console.log(res);
    let html = conv.makeHtml(res.text());
    addMessage(html, "start");
}
const addMessage = (msg, direction) => {
    const messageHolder = document.getElementById("messageHolder");
    const message = document.createElement("div");
    const colour = direction !== "start" ? "blue" : "green";
    message.innerHTML = `
	<div class="flex flex-col items-${direction}">
			<div class="bg-${colour}-500 px-4 py-2 rounded-md text-white w-fit 
			max-w-4xl mb-1">${msg}</div>
		</div>
	`
    messageHolder.appendChild(message);
}

const messageInput = document.getElementById("chat");
const sendBtn = document.getElementById("btn");

sendBtn.addEventListener("click", function () {
    const message = messageInput.value;
    chatGemini(message);
    messageInput.value = "";
});

window.onload = async () => {
    console.log('The Script will load now.');
    let msg = "This chatbot is part of a bus booking system, so you will answer only those questions related to bus stuff, anything else state - This chatbot can answer questions only about bus booking...."
    msg += "Further information about us: Website is built using Flask Framework, HTML/CSS/JS frontend and Python Flask backend, with MYSQL database. All CRUD operations take place in the website."
    msg += "Advanced libraries like sqlalchemy has been used for database connectivity. Jinja has been used as a templating tool. MongoDB has also been incorporated for user reviews through pymongo. Following this is the jknowledge base of the project. You can use only this information and general information about flask and web development in general."
    msg += `Introduction :
            In the Indian context, the need for automated bus booking systems arises from the country’s vast 
            geographical expanse and a large population dependent on public transportation.Manual ticket 
            booking processes are often time - consuming, prone to errors, and lack real - time updates on seat 
            availability and schedules.By automating these processes, the bus booking portal aims to streamline 
            ticket reservations, reduce booking errors, and enhance overall user satisfaction, catering to the 
            diverse travel needs of passengers across India efficiently.
            The scope of this project includes developing a web - based platform where users can search for bus 
            routes, view available seats, select preferred timings, and make secure online payments for their 
            tickets.The portal will also allow users to manage their bookings, view past transactions, and 
            receive notifications about their journey.
            The objective of this project is to create a user - friendly and efficient bus booking portal using the 
            Python Flask Framework integrated with a MySQL database.The portal aims to automate the 
            process of booking bus tickets in India, providing users with a seamless and convenient experience.
            `
    msg += `Entity Relationship Diagram
            In our bus booking project, the Entity Relationship (ER) diagram plays a crucial role in illustrating 
            how different components of the system are interconnected. An ER diagram is like a map that shows 
            how entities (like Users, Accounts, Buses, Posts, and Orders) in our system relate to each other.
            Users represent individuals using our booking system, while Accounts store their relevant 
            information. Buses and Posts are essential entities providing details about available buses and their 
            schedules/routes, respectively. Orders are created when users book tickets through the system.
            The ER diagram visually represents how users are associated with their accounts, how buses and 
            posts are linked to facilitate booking, and how orders are connected to users and their booked trips. 
            Understanding these relationships is crucial for designing an efficient and user-friendly system. It 
            helps developers and stakeholders comprehend data flow, system behavior, and the overall structure 
            of the bus booking platform, ensuring seamless interactions and satisfying user experiences.`
    msg += `Relational Schema:
            The relational schema defines how data is organized and related in our MySQL database. We have 
            tables such as Users, Accounts, Buses, Posts, and Orders, each representing different entities in our 
            system. For example, the Users table stores user information like names and contact details, while 
            the Orders table keeps track of bookings made by users.
            Normalization:
            Normalization is the process of structuring data in a database to reduce redundancy and improve 
            data integrity. We follow normalization principles up to the third normal form (3NF) to ensure our 
            database is well-organized and optimized.
            1. First Normal Form (1NF):
            We ensure that each table has atomic values in each column, meaning no multi-valued attributes or 
            repeating groups. For instance, user details like names and addresses are stored in separate columns 
            instead of a single column.
            2. Second Normal Form (2NF):
            Tables are in 2NF when they are in 1NF and have no partial dependencies. We eliminate partial 
            dependencies by separating related data into different tables. For example, user information related 
            to bookings is stored in the Orders table instead of the Users table.
            3. Third Normal Form (3NF):
            Tables are in 3NF when they are in 2NF and have no transitive dependencies. We further break 
            down tables to remove transitive dependencies and ensure data integrity. For instance, we separate 
            information about buses and their routes into distinct tables to avoid duplication and maintain 
            consistency.`
    msg += `Detailed Design :
            The Data Flow Diagram (DFD) is a visual representation that shows how data moves through 
            different parts of our bus booking system. It helps us understand how information flows between 
            various components, making it easier to design and manage the system effectively.
            In our DFD, we have two main levels: Level 0 and Level 1. In Level 0, we have a single block 
            representing the Bus Reservation System. This block is connected to two external entities: the 
            Company and the Customer. This level gives us a high-level view of how the system interacts 
            with its external entities.
            Moving to Level 1 of our DFD, we have a more detailed breakdown of the system. Here, we 
            introduce a Central Database block connected to several processes and entities. These include 
            managing customer information, managing transactions, connecting with customers, and 
            interacting with the company. The Central Database acts as a hub where all crucial information is 
            stored and accessed by different parts of the system.
            By creating this DFD, we can clearly see how data flows from external entities into the Bus 
            Reservation System, how it is processed and stored in the Central Database, and how it is utilized 
            for managing customer information, transactions, and interactions with the company. This 
            diagram helps us identify potential bottlenecks, streamline data handling processes, and ensure 
            smooth communication and data management throughout the bus booking system.`
    msg += `NoSQL Integration: In our bus booking project, we have integrated a NoSQL database, specifically MongoDB, to handle 
            user queries and reviews efficiently. NoSQL databases like MongoDB play a crucial role in modern 
            web applications due to their flexible and scalable nature.
            Unlike traditional relational databases, NoSQL databases like MongoDB can store and manage 
            unstructured or semi-structured data, making them ideal for handling user-generated content such 
            as reviews, comments, and queries in our bus booking portal. MongoDB's document-oriented 
            approach allows us to store data in JSON-like documents, which closely aligns with the data format 
            commonly used in web applications.
            MongoDB's scalability and ability to handle large volumes of data make it suitable for our project, 
            where users can post reviews, ask questions, and interact dynamically with the system. Its fast read 
            and write operations ensure quick access to user-generated content, enhancing the overall user 
            experience.
            By leveraging MongoDB in our project, we can efficiently manage user queries and reviews, store 
            them in a structured format, and retrieve them seamlessly when needed. This improves the 
            responsiveness of our system and allows us to adapt to changing user needs and data volumes 
            without compromising performance.`

    msg += `Conclusion & Future Enhancement: 
            Our bus booking portal project has been a significant endeavor aimed at streamlining the process of 
            booking bus tickets in India. Through the implementation of technologies like Flask, MySQL, 
            MongoDB, and frontend technologies such as HTML, CSS, and JavaScript, we have created a userfriendly platform that offers several key features to enhance the user experience.
            The use of a client-server architecture with Flask as the backend framework has allowed for efficient 
            data management and processing. MySQL and MongoDB databases have been instrumental in 
            storing and retrieving both relational and NoSQL data, ensuring seamless interactions for users. 
            Additionally, the integration of HTML, CSS, and JavaScript has resulted in a responsive and 
            interactive user interface, making it easy for users to navigate and book tickets effortlessly.
            The inclusion of user authentication features, data storage and retrieval mechanisms, and frontend 
            interactivity has significantly contributed to the usefulness of our project. Users can register, log in 
            securely, view bus routes, check seat availability, and make bookings with ease.
            Looking ahead, there are several avenues for future work to enhance the system further. One crucial 
            aspect to consider is implementing real-time updates through GPS technology. This would enable 
            users to track buses in real-time, providing accurate information about bus locations, arrival times, 
            and delays. Integrating GPS data into our system would require developing robust APIs, 
            implementing efficient data processing algorithms, and ensuring seamless integration with our 
            existing platform.
            Overall, our bus booking portal has laid a solid foundation for a convenient and efficient booking 
            experience. With continued enhancements and future developments like real-time GPS updates, we 
            aim to further improve user satisfaction and meet the evolving needs of travelers in India.`
    console.log(msg)
    let res = await chat.sendMessage(msg);
    res = await res.response.text()
    console.log(res)

}