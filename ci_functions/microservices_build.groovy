def call(serviceName, dockerRepoName, imageName) {
    pipeline { 
    agent any  
    stages { 
        stage('Python Lint') {
            steps {
                    sh "pylint-fail-under --fail_under 5.0 ${serviceName}/*.py"    
            }  
        }
        stage('Package') { 
            when { 
                expression { env.GIT_BRANCH == 'origin/main' } 
            } 
            steps { 
                withCredentials([string(credentialsId: 'nlai15', variable: 'TOKEN')]) {
                    sh "docker login -u 'ijazhussain' -p '$TOKEN' docker.io" 
                    sh "docker build -t ${dockerRepoName}:latest --tag nlai15/${dockerRepoName}:${imageName} ${serviceName}" 
                    sh "docker push ijazhussain/${dockerRepoName}:${imageName}" 
                } 
            } 
        }
        stage('Anchore Image Scan') {
            steps {
                sh "echo 'docker.io/nlai15/${dockerRepoName}:${imageName} ${serviceName}/Dockerfile' > anchore_images"
                anchore name: 'anchore_images', forceAnalyze: 'true'
            }  
        } 
    }
}
}
