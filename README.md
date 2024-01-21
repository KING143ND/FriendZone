# FriendZone

Welcome to FriendZone! FriendZone is a Django-based social networking platform where users can connect, share updates, and interact with friends.

![FriendZone]

## Live Demo

Explore the live demo of FriendZone: [FriendZone Live](https://king143nd.pythonanywhere.com/)

Feel free to check out the live project and experience these functionalities in action!

# Functionality

FriendZone is a comprehensive social networking platform with a range of features to enhance user interaction. Below are some of the key functionalities:

## 1. User Authentication and Authorization

- **Registration:** Users can register for an account on FriendZone by providing necessary details.
- **Login:** Registered users can log in using their credentials.
- **Authentication:** Secure authentication ensures user accounts are protected.

## 2. Profile Management

- **User Profiles:** Users can create and customize their profiles with personal information, profile pictures, and more.
- **Timeline:** A dynamic timeline where users can share updates, photos, and interact with posts.
- **Follow/Unfollow System:** Users can follow and unfollow other users to curate their timeline.
- **Follower/Following List:** View a list of followers and users being followed.

## 3. Visual Content Sharing

- **Photo Sharing:** Users can upload and share photos with captions and tags on their profiles.
- **Like and Comment:** Interact with posts by liking and commenting on them.
- **Explore Feed:** Discover new content through an explore feed based on user interests.
- **Private Messaging:** Send private messages to friends within the platform.
- **Tag System:** Add tags to new posts and view all related posts in a specific tag view.

## 4. Follow System

- **Follow Users:** Users can follow other users to see their posts in their timeline.
- **Unfollow Users:** Easily unfollow users to adjust the content in the timeline.

## 5. Notifications

- **Real-time Notifications:** Receive notifications for new followers, likes, comments and messages.

## 6. Search Functionality

- **Search Users:** Search for specific users using usernames or other parameters.
- **Search Tags:** Search for specific tags and view related posts.

## 7. Responsive Design

- **Mobile-Friendly:** The application is designed to be responsive, ensuring a consistent experience across devices.

## Getting Started

To run this project locally, follow these steps:

1. Clone this repository:

    ```bash
    git clone https://github.com/KING143ND/FriendZone.git
    ```

2. Navigate to the project directory:

    ```bash
    cd FriendZone
    ```

3. Create and activate a virtual environment (replace `env` with your preferred name):

    ```bash
    # On Windows
    python -m venv env
    ./env/Scripts/activate

    # On macOS and Linux
    python -m venv env
    source env/bin/activate
    ```

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Apply migrations:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. Start the development server:

    ```bash
    python manage.py runserver
    ```

7. Open your browser and visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Contributing

If you'd like to contribute to this project, please follow the guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

1. Fork the repository.

2. Create a new branch for your feature or bug fix:

    ```bash
    git checkout -b feature/my-feature
    ```

3. Make your changes and commit them:

    ```bash
    git commit -m "Add my feature"
    ```

4. Push to your fork:

    ```bash
    git push origin feature/my-feature
    ```

5. Create a pull request.


## License

This project is licensed under the [MIT License](LICENSE).

## Contact

If you have any questions or suggestions, feel free to reach out at [nvnaveenchaudhary@gmail.com](mailto:nvnaveenchaudhary@gmail.com).

Happy networking!
