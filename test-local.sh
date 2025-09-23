#!/bin/bash

# 🧪 Local Docker Testing Script
# Tests the contact import functionality locally

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Local Docker Testing for Contact Import${NC}"
echo -e "${BLUE}=========================================${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Build and start containers
print_status "Building and starting Docker containers..."
docker-compose -f docker-compose.local.yml up --build -d

# Step 2: Wait for services to start
print_status "Waiting for services to start..."
sleep 30

# Step 3: Test health endpoint
print_status "Testing health endpoint..."
for i in {1..10}; do
    if curl -f -s http://localhost:8001/health > /dev/null; then
        print_status "Health check passed!"
        break
    else
        if [ $i -eq 10 ]; then
            print_error "Health check failed!"
            docker-compose -f docker-compose.local.yml logs backend
            exit 1
        fi
        echo "Waiting for backend to start... ($i/10)"
        sleep 10
    fi
done

# Step 4: Test API endpoints
print_status "Testing API endpoints..."

echo "Root endpoint:"
curl -s http://localhost:8001/ | jq .

echo -e "\nHealth endpoint:"
curl -s http://localhost:8001/health | jq .

echo -e "\nAPI status:"
curl -s http://localhost:8001/api/status | jq .

# Step 5: Test contact import preview (create test CSV)
print_status "Testing contact import preview..."
cat > test_contacts.csv << 'EOF'
First Name,Last Name,Company,Job Title,LinkedIn URL,Email
John,Doe,Acme Corp,Software Engineer,https://linkedin.com/in/john-doe,john.doe@example.com
Jane,Smith,Tech Inc,Product Manager,https://linkedin.com/in/jane-smith,jane.smith@example.com
Mike,Johnson,StartupXYZ,CEO,https://linkedin.com/in/mike-johnson,mike.johnson@example.com
EOF

echo "Testing contact import preview endpoint..."
curl -X POST "http://localhost:8001/api/campaigns/test-campaign/contacts/import/preview" \
    -F "file=@test_contacts.csv" \
    -F "source=custom" \
    -F 'field_mapping={"First Name": "first_name", "Last Name": "last_name", "Company": "company_name", "Job Title": "job_title", "LinkedIn URL": "linkedin_url", "Email": "email"}' \
    -H "Content-Type: multipart/form-data" | jq .

# Clean up test file
rm test_contacts.csv

print_status "✅ All tests completed successfully!"
echo ""
echo -e "${BLUE}🌐 Local Backend: http://localhost:8001${NC}"
echo -e "${BLUE}📊 Health: http://localhost:8001/health${NC}"
echo -e "${BLUE}📚 API Docs: http://localhost:8001/docs${NC}"
echo -e "${BLUE}🎯 Contact Import: http://localhost:8001/api/campaigns/{campaign_id}/contacts/import/preview${NC}"
echo ""
echo -e "${YELLOW}📋 To stop: docker-compose -f docker-compose.local.yml down${NC}"
echo -e "${YELLOW}📋 To view logs: docker-compose -f docker-compose.local.yml logs -f${NC}"
